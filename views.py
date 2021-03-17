import json

from django.http import JsonResponse
from django.views.generic import View
from rc_protocol import validate_checksum

from django.conf import settings


class PostApiPoint(View):

    required_parameters: list
    endpoint: str

    def post(self, request, *args, **kwargs):
        # Decode json
        try:
            parameters = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Decoding data failed"},
                status=400,
                reason="Decoding data failed"
            )

        # Validate checksum
        try:
            if not validate_checksum(parameters, settings.SHARED_SECRET,
                                     self.endpoint, settings.SHARED_SECRET_TIME_DELTA):
                return JsonResponse(
                    {"success": False, "message": "Checksum was incorrect."},
                    status=400,
                    reason="Checksum was incorrect."
                )
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "No checksum was given."},
                status=400,
                reason="No checksum was given."
            )

        # Check required parameters
        for param in self.required_parameters:
            if param not in parameters:
                return JsonResponse(
                    {"success": False, "message": f"Parameter {param} is mandatory but missing."},
                    status=400,
                    reason=f"Parameter {param} is mandatory but missing."
                )

        # Hand over to subclass
        return self.safe_post(request, parameters, *args, **kwargs)

    def safe_post(self, request, parameters, *args, **kwargs):
        return NotImplemented
