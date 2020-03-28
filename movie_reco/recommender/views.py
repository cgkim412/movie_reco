from django.utils.decorators import method_decorator
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.decorators import login_required
from accounts.utils import get_user_obj
from recommender.reco_interface import RECO_INTERFACE


@method_decorator(login_required, name='dispatch')
class RecoListAPI(APIView):
    def get(self, request, limit=100):
        user = get_user_obj(request)
        reco_list = RECO_INTERFACE.get_recommendation(user, limit=min(100, limit))

        res_data = []
        for label, items in reco_list.items():
            entry = {"label": label, "items": items}
            res_data.append(entry)
        json = JSONRenderer().render(res_data)
        return Response(json)

