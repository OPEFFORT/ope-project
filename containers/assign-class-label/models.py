from pydantic import BaseModel, constr
from typing import Dict, Optional


class PodMetadata(BaseModel):
    labels: Optional[Dict[str, str]] = None


class PodObject(BaseModel):
    metadata: PodMetadata


class AdmissionRequest(BaseModel):
    uid: constr(min_length=1)
    object: PodObject


class AdmissionReview(BaseModel):
    request: AdmissionRequest


class Status(BaseModel):
    message: Optional[str] = None


class AdmissionResponse(BaseModel):
    uid: str
    allowed: bool
    status: Optional[Status] = None
    patchType: Optional[str] = None
    patch: Optional[str] = None


class AdmissionReviewResponse(BaseModel):
    apiVersion: str = 'admission.k8s.io/v1'
    kind: str = 'AdmissionReview'
    response: AdmissionResponse
