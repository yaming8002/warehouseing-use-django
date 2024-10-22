
from datetime import datetime
import re
import zipfile
import fitz  # PyMuPDF
from io import BytesIO
from django.utils.encoding import escape_uri_path
from django.shortcuts import render
from django.http import  HttpResponse, JsonResponse
import os
from django.db.models import Max
from django.utils.timezone import now
import base64
from stock.models.pdf_report import PDFileModel
from stock.models.site_model import SiteInfo
from warehousing_server import settings
from wcom.utils.uitls import get_month_range


def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        # 定義上傳檔案的存放路徑
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filename = pdf_file.name
        site_code = filename[:4]  # 假設文件名的前4個字符為 site_code
        try:
            site_info = SiteInfo.objects.get(code=site_code)
        except SiteInfo.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f"無法找到對應的站點資訊：{site_code}"
            })

        # 儲存檔案
        # 获取当前 site_info 下的最大版本号
        current_max_version = PDFileModel.objects.filter(siteinfo=site_info).aggregate(Max('version'))['version__max']

        # 如果没有任何版本，设为 1，否则递增
        version_count = 1 if current_max_version is None else current_max_version + 1
        file_path = os.path.join(upload_dir,f'{version_count}-{pdf_file.name}')
        with open(file_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        # 將 PDF 文件的相關資訊儲存至資料庫
        PDFileModel.objects.create(
            siteinfo=site_info,
            version=version_count,
            file_path=file_path
        )

        # 返回成功的回應
        return JsonResponse({
            'success': True,
            "images": get_base64_images(file_path),
            'upload_time': now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # GET 請求，渲染上傳 PDF 檔案的表單頁面
    if request.method == 'GET':
        return render(request, 'dff_report/pdf_report_upload.html')

    # 若沒有正確的 POST 請求，返回錯誤信息
    return JsonResponse({'success': False, 'message': '上傳失敗，請提供正確的 PDF 檔案'})

def report_end_view(request):
    # 将查询结果传递给模板
    pdfs ={}
    context={}
    if request.method == "POST":
        code = request.POST.get("site_code")
        context["constn"] = SiteInfo.get_site_by_code(code)
        pdf_list = PDFileModel.objects.filter(siteinfo=context["constn"]).order_by('-id')
        for pdf in pdf_list:
            # 將該 PDF 的內容存入字典，以 pdf_id 為鍵
            pdfs[pdf.id]=get_base64_images(pdf.file_path)

    context["pdfs"] = pdfs
    context["total_pages"] = len(pdfs)

    return render(request, "dff_report/pdf_list.html", context)

def report_remove(request):
    if request.method == "GET":
        pdf_id = request.GET.get("pdf_id")
        pdf = PDFileModel.objects.get(id=pdf_id)
        os.remove(pdf.file_path)
        pdf.delete()

    return JsonResponse({"success": True, "msg": "刪除成功"})

def report_download_by_month(request):
    # 1. 獲取當月範圍
    first_day, last_day = get_month_range()

    # 2. 查詢當月的 PDF 列表
    pdf_list = PDFileModel.objects.filter(build_date__gte=first_day, build_date__lte=last_day).order_by('-id')

    # 3. 定義 ZIP 文件的名稱
    zip_filename = f'{first_day.year}-{first_day.month}-pdf.zip'

    # 4. 創建 ZIP 文件
    with zipfile.ZipFile(zip_filename, 'w') as zf:
        for pdf in pdf_list:
            # 獲取每個 PDF 文件的絕對路徑並寫入 ZIP 文件
            filter_names = pdf.file_path.split('\\')
            arcname = filter_names[-1]
            zf.write(pdf.file_path,arcname=arcname)

    # 5. 打開 ZIP 文件並返回作為 HttpResponse
    with open(zip_filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        # 設置下載的文件名，使用 escape_uri_path 防止中文亂碼
        response['Content-Disposition'] = f'attachment; filename={escape_uri_path(zip_filename)}'

    # 6. 刪除臨時 ZIP 文件（可選）
    os.remove(zip_filename)

    return response

def report_download_by_site(request, contsn_code):
    # 1. 獲取 PDF 的 id
    site = SiteInfo.get_site_by_code(contsn_code)
    pdf_list = PDFileModel.objects.filter(siteinfo=site).order_by('-id')

    # 3. 定義 ZIP 文件的名稱
    zip_filename = f'{site.code}-{site.owner}-{site.name}-pdf.zip'

    # 4. 創建 ZIP 文件
    with zipfile.ZipFile(zip_filename, 'w') as zf:
        for pdf in pdf_list:
            # 獲取每個 PDF 文件的絕對路徑並寫入 ZIP 文件
            filter_names = pdf.file_path.split('\\')
            arcname = filter_names[-1]
            zf.write(pdf.file_path,arcname=arcname)

    # 5. 打開 ZIP 文件並返回作為 HttpResponse
    with open(zip_filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        # 設置下載的文件名，使用 escape_uri_path 防止中文亂碼
        response['Content-Disposition'] = f'attachment; filename={escape_uri_path(zip_filename)}'

    # 6. 刪除臨時 ZIP 文件（可選）
    os.remove(zip_filename)
    return response

def get_base64_images(file_path):
    pdf_document = fitz.open(file_path)
    dpi = 150  # 你可以調整這個 DPI 值

    # A4 尺寸的比例
    scale = dpi / 72  # 原 PDF 的標準 DPI 為 72，使用這個比值來縮放
    mat = fitz.Matrix(scale, scale)  # 創建一個縮放矩陣

    # 用於存放 base64 編碼的圖像
    base64_images = []

    # 遍歷每一頁，轉換為圖像
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)  # 加載頁面
        pix = page.get_pixmap(matrix=mat)  # 使用縮放矩陣生成 Pixmap

        # 將圖像保存到內存中
        img_buffer = BytesIO()
        img_buffer.write(pix.tobytes())  # 使用 `tobytes()` 直接獲取圖像的二進制數據
        img_buffer.seek(0)  # 重置指針到文件開始

        # 將圖像轉換為 Base64
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        base64_images.append(img_str)
    return base64_images
