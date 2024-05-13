
from trans.forms import CarinfoFrom
from trans.models import CarInfo
from wcom.utils.excel_tool import ImportData2Generic
from wcom.utils.pagelist import PageListView
from wcom.utils.save_control import SaveControlView
from wcom.utils.uitls import excel_value_to_str


class CarListView(PageListView):
    model = CarInfo
    template_name = "trans/carinfo.html"
    title_name = "車輛清單"

    def get_queryset(self):
        result = CarInfo.objects
        car_number = self.request.GET.get("car_number")
        firm = self.request.GET.get("firm")

        group = self.request.GET.get("group")
        if car_number:
            result = result.filter(car_number__istartswith=car_number)
        if group:
            result = result.filter(is_count=(group == "1"))
        elif firm:
            result = result.filter(firm__startswith=firm)

        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CarInfoControlView(SaveControlView):
    name = "車輛資訊"
    model = CarInfo
    form_class = CarinfoFrom

    def form_is_valid(self ,form):
        form.instance.is_count = form.cleaned_data.get('is_count', False)



class ImportCarInfoView(ImportData2Generic):
    title = "上傳EXCEL"
    action = "/carinfo/uploadexcel/"
    columns = ["車牌號碼", "吊卡車公司", "噸數(備註)", "基本台金"]

    def insertDB(self, item):
        if item[0] is None:
            return 
        code = excel_value_to_str(item[0])
        firm = item[1]
        
        if CarInfo.objects.filter(car_number=code, firm=firm).exists():
            print(f"{code},{firm} is exists")
        else:
            CarInfo.create(
                car_number=code,
                firm=firm,
                remark=item[2],
                value=item[3],
            )


class ImportCarInfoByTotalView(ImportData2Generic):
    def insertDB(self, item):
        if  "car_number" not in item.keys() :
            return
        car_number = f"{item['car_number']}"
        remark = f"{item.get('remark', '')},{item.get('value', '')}"
        firm =f"{item.get('car_firm', '')}"

        CarInfo.objects.get_or_create(
            car_number =car_number,
            firm=firm,
            defaults={
                "remark":remark
            }
        )
        
        # if CarInfo.objects.filter(car_number=item['car_number']).exists():
        #     CarInfo.objects.filter(car_number=item['car_number']).update(
        #         firm=firm,
        #         remark=remark
        #     )
        # else :
        #     CarInfo.objects.create(
        #         car_number =item['car_number'],
        #         firm=item['car_firm'] if "car_firm" in item.keys() else "",
        #         remark=remark
        #     )

 