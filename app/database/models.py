"""Import every mapped table once for migrations and workers."""

from app.modules.audit.models import *  # noqa: F403
from app.modules.clinical_records.models import *  # noqa: F403
from app.modules.consent.models import *  # noqa: F403
from app.modules.consultations.models import *  # noqa: F403
from app.modules.dispensing.models import *  # noqa: F403
from app.modules.documents.models import *  # noqa: F403
from app.modules.identity.models import *  # noqa: F403
from app.modules.integrations.models import *  # noqa: F403
from app.modules.measurements.models import *  # noqa: F403
from app.modules.medication.models import *  # noqa: F403
from app.modules.notifications.models import *  # noqa: F403
from app.modules.organizations.models import *  # noqa: F403
from app.modules.prescriptions.models import *  # noqa: F403
from app.modules.profiles.models import *  # noqa: F403
from app.modules.vaccinations.models import *  # noqa: F403
from app.modules.verification.models import *  # noqa: F403
