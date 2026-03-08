from src.models.auth import User
from src.models.doctor import DoctorQualificationDocument, Specialization
from src.models.qa import Question, QuestionComment
from src.schemas.auth import SpecializationInlineDTO, UserProfileDTO
from src.schemas.doctor import DoctorDetailDTO, DoctorListItemDTO, DoctorQualificationDocumentDTO, SpecializationDTO
from src.schemas.qa import QuestionCommentDTO, QuestionDTO, UserShortDTO


def to_specialization_dto(item: Specialization) -> SpecializationDTO:
    return SpecializationDTO.model_validate(item)


def to_user_profile(user: User) -> UserProfileDTO:
    return UserProfileDTO(
        id=user.id,
        username=user.username,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified_doctor=user.is_verified_doctor,
        specializations=[
            SpecializationInlineDTO(id=spec.id, name=spec.name)
            for spec in sorted(user.specializations, key=lambda item: item.name.lower())
        ],
        qualification_documents_count=len(user.qualification_documents),
    )


def to_document_dto(document: DoctorQualificationDocument) -> DoctorQualificationDocumentDTO:
    return DoctorQualificationDocumentDTO(
        id=document.id,
        original_file_name=document.original_file_name,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
        created_at=document.created_at,
    )


def to_doctor_list_item(user: User) -> DoctorListItemDTO:
    return DoctorListItemDTO(
        id=user.id,
        username=user.username,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified_doctor=user.is_verified_doctor,
        specializations=[to_specialization_dto(spec) for spec in sorted(user.specializations, key=lambda item: item.name.lower())],
    )


def to_doctor_detail(user: User) -> DoctorDetailDTO:
    return DoctorDetailDTO(
        **to_doctor_list_item(user).model_dump(),
        qualification_documents=[
            to_document_dto(item) for item in sorted(user.qualification_documents, key=lambda doc: doc.created_at, reverse=True)
        ],
    )


def to_user_short(user: User) -> UserShortDTO:
    return UserShortDTO(
        id=user.id,
        username=user.username,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified_doctor=user.is_verified_doctor,
    )


def to_question_comment(comment: QuestionComment) -> QuestionCommentDTO:
    return QuestionCommentDTO(
        id=comment.id,
        text=comment.text,
        created_at=comment.created_at,
        author=to_user_short(comment.author),
    )


def to_question(question: Question) -> QuestionDTO:
    comments = sorted(question.comments, key=lambda item: item.created_at)
    return QuestionDTO(
        id=question.id,
        text=question.text,
        created_at=question.created_at,
        author=to_user_short(question.author),
        comments=[to_question_comment(item) for item in comments],
    )
