from database.models.user import User, UserRole
from database.models.lead import Lead, LeadStatus
from database.models.appointment import Appointment, AppointmentStatus
from database.models.learning import Module, Task, TaskProgress
from database.models.payment import Payment, PaymentStatus
all_models=(User, Lead, Appointment, Module, Task, TaskProgress, Payment)
