#later use this analyis engibe @api_view(['POST'])

from .models import AdvisorAuth

def sync():
    for adv in Advisor.objects.using('client_db').all():
        advisor_name = adv.advisor_name
        advisor_id = adv.advisor_id
        class_id = adv.class_id

        if not AdvisorAuth.objects.filter(advisor_id=advisor_id).exists():
            auth = AdvisorAuth(advisor_id=advisor_id, advisor_name=advisor_name,class_id=class_id)
            auth.save()

    return {'message': 'synced'}