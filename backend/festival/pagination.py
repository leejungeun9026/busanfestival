from rest_framework.pagination import PageNumberPagination

class FestivalPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"     # ?size=20
    max_page_size = 100

    def get_page_size(self, request):
        # size가 오면 우선 사용
        size = request.query_params.get("size")
        if size is not None:
            try:
                size = int(size)
                return min(size, self.max_page_size)
            except ValueError:
                pass
        return super().get_page_size(request)
