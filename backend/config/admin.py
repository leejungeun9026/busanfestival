from django.contrib.admin import AdminSite
from django.contrib.admin.sites import site as default_site


class CustomAdminSite(AdminSite):

	def get_app_list(self, request, app_label=None):
		app_list = super().get_app_list(request, app_label)

		for app in app_list:
			if app["app_label"] == "festival":
				order = {
					"축제 데이터 동기화 로그": 1,
					"축제 데이터 원본 목록": 2,
					"축제 데이터 운영용 목록": 3,
				}
				app["models"].sort(key=lambda m: order.get(m["name"], 999))
		return app_list

custom_admin_site = CustomAdminSite(name="custom_admin")
# 기존의 @admin.register 로 등록된 데이터 그대로 가져오기
for model, model_admin in default_site._registry.items():
	custom_admin_site.register(model, model_admin.__class__)