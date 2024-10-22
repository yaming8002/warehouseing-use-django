
import fitz  # PyMuPDF
from io import BytesIO
from django.shortcuts import render
from django.http import  JsonResponse
import os
from django.utils.timezone import now
import base64
from stock.models.pdf_report import PDFileModel
from stock.models.site_model import SiteInfo
from warehousing_server import settings


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
        version_count = PDFileModel.objects.filter(siteinfo=site_info).count() + 1
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
