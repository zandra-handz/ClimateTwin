import coreapi
import coreschema
from rest_framework.schemas import AutoSchema, ManualSchema

post_go_schema = AutoSchema(manual_fields=[
    coreapi.Field("address", required=True, location="form", type="string", description="Address to validate")
])