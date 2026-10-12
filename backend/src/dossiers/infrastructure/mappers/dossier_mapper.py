"""Mapping entre les entités domaine dossiers et les modèles ORM SQLAlchemy."""

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn

from src.dossiers.infrastructure.orm.dossier_model import DossierModel
from src.dossiers.infrastructure.orm.financing_plan_model import FinancingPlanModel
from src.dossiers.infrastructure.orm.trade_in_model import TradeInModel


class DossierMapper:
    """Convertit un agrégat Dossier en modèle ORM et inversement."""

    @staticmethod
    def to_domain(model: DossierModel) -> Dossier:
        """Reconstruit un dossier domaine depuis son modèle SQLAlchemy."""
        trade_in = None
        if model.trade_in is not None:
            trade_in = TradeIn(
                registration=model.trade_in.registration,
                mileage=model.trade_in.mileage,
                brand=model.trade_in.brand,
                model=model.trade_in.model,
                estimated_value=model.trade_in.estimated_value,
            )

        financing_plan = None
        if model.financing_plan is not None:
            financing_plan = FinancingPlan(
                down_payment=model.financing_plan.down_payment,
                duration_months=model.financing_plan.duration_months,
                monthly_payment=model.financing_plan.monthly_payment,
            )

        return Dossier(
            id=model.id,
            user_id=model.user_id,
            vehicle_id=model.vehicle_id,
            status=model.status,
            trade_in=trade_in,
            financing_plan=financing_plan,
            upload_started_at=model.upload_started_at,
            submitted_at=model.submitted_at,
            rejected_at=model.rejected_at,
            comment=model.comment,
            rejection_reason=model.rejection_reason,
            requested_document_types=model.requested_document_types,
            validated_by_admin_id=model.validated_by_admin_id,
            rejected_by_admin_id=model.rejected_by_admin_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_orm(
        dossier: Dossier,
        existing_model: DossierModel | None = None,
    ) -> DossierModel:
        """Convertit un dossier domaine en modèle SQLAlchemy."""
        model = existing_model or DossierModel()
        model.id = dossier.id
        model.user_id = dossier.user_id
        model.vehicle_id = dossier.vehicle_id
        model.status = dossier.status
        model.upload_started_at = dossier.upload_started_at
        model.submitted_at = dossier.submitted_at
        model.rejected_at = dossier.rejected_at
        model.comment = dossier.comment
        model.rejection_reason = dossier.rejection_reason
        model.requested_document_types = dossier.requested_document_types
        model.validated_by_admin_id = dossier.validated_by_admin_id
        model.rejected_by_admin_id = dossier.rejected_by_admin_id
        model.created_at = dossier.created_at
        model.updated_at = dossier.updated_at

        # Mapping TradeIn
        if dossier.trade_in is not None:
            if model.trade_in is None:
                model.trade_in = TradeInModel(dossier_id=dossier.id)
            model.trade_in.registration = dossier.trade_in.registration
            model.trade_in.mileage = dossier.trade_in.mileage
            model.trade_in.brand = dossier.trade_in.brand
            model.trade_in.model = dossier.trade_in.model
            model.trade_in.estimated_value = dossier.trade_in.estimated_value
        else:
            model.trade_in = None

        # Mapping FinancingPlan
        if dossier.financing_plan is not None:
            if model.financing_plan is None:
                model.financing_plan = FinancingPlanModel(dossier_id=dossier.id)
            model.financing_plan.down_payment = dossier.financing_plan.down_payment
            model.financing_plan.duration_months = (
                dossier.financing_plan.duration_months
            )
            model.financing_plan.monthly_payment = (
                dossier.financing_plan.monthly_payment
            )
        else:
            model.financing_plan = None

        return model
