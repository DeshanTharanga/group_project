CREATE TYPE account_status AS ENUM ('pending', 'active', 'suspended', 'disabled');

CREATE TYPE clinical_record_status AS ENUM ('active', 'superseded', 'withdrawn');

CREATE TYPE document_status AS ENUM ('active', 'superseded', 'withdrawn');

CREATE TYPE dose_response AS ENUM ('taken', 'skipped');

CREATE TYPE dose_status AS ENUM ('upcoming', 'due', 'taken', 'skipped', 'unreported', 'cancelled');

CREATE TYPE entity_status AS ENUM ('pending', 'active', 'suspended', 'rejected', 'inactive');

CREATE TYPE grant_category AS ENUM ('history_allergies', 'prescriptions', 'reports', 'measurements_vaccinations', 'adherence');

CREATE TYPE grant_status AS ENUM ('active', 'revoked', 'expired');

CREATE TYPE idempotency_actor_type AS ENUM ('user', 'client');

CREATE TYPE integration_status AS ENUM ('pending', 'active', 'suspended', 'revoked');

CREATE TYPE measurement_status AS ENUM ('active', 'superseded', 'withdrawn');

CREATE TYPE measurement_type AS ENUM ('weight', 'blood_pressure', 'blood_glucose');

CREATE TYPE organization_type AS ENUM ('clinic', 'hospital', 'pharmacy', 'laboratory', 'other');

CREATE TYPE prescription_ocr_job_status AS ENUM ('queued', 'processing', 'ready_for_review', 'failed', 'draft_created');

CREATE TYPE prescription_review_status AS ENUM ('not_reviewed', 'reviewed', 'needs_clarification', 'not_accepted');

CREATE TYPE prescription_source AS ENUM ('patient', 'doctor');

CREATE TYPE prescription_status AS ENUM ('draft', 'active', 'completed', 'discontinued', 'cancelled', 'superseded');

CREATE TYPE prescription_template_status AS ENUM ('active', 'archived');

CREATE TYPE prescription_template_type AS ENUM ('favourite', 'template');

CREATE TYPE professional_role AS ENUM ('doctor', 'pharmacist', 'lab_staff');

CREATE TYPE record_source AS ENUM ('patient', 'doctor', 'laboratory', 'integration');

CREATE TYPE report_status AS ENUM ('active', 'superseded', 'withdrawn');

CREATE TYPE review_outcome AS ENUM ('reviewed', 'needs_clarification', 'not_accepted');

CREATE TYPE schedule_status AS ENUM ('active', 'paused', 'completed', 'cancelled');

CREATE TYPE share_status AS ENUM ('created', 'claimed', 'confirmed', 'expired', 'revoked');

CREATE TYPE submission_status AS ENUM ('received', 'accepted', 'rejected', 'failed');

CREATE TYPE upload_request_status AS ENUM ('active', 'used', 'revoked', 'expired');

CREATE TYPE verification_status AS ENUM ('not_submitted', 'pending', 'approved', 'rejected', 'more_info_requested', 'suspended');


CREATE TABLE api_idempotency_records (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	actor_type idempotency_actor_type NOT NULL,
	actor_id UUID NOT NULL,
	operation_key TEXT NOT NULL,
	target_key TEXT DEFAULT '-'::text NOT NULL,
	idempotency_key TEXT NOT NULL,
	request_digest TEXT NOT NULL,
	response_status SMALLINT NOT NULL,
	response_body JSONB NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
	CONSTRAINT api_idempotency_records_pkey PRIMARY KEY (id),
	CONSTRAINT uq_idempotency_scoped_key UNIQUE (actor_type, actor_id, operation_key, target_key, idempotency_key),
	CONSTRAINT ck_idempotency_digest CHECK (request_digest ~ '^[0-9a-fA-F]{64}$'::text),
	CONSTRAINT ck_idempotency_status CHECK ((response_status >= 200) AND (response_status <= 299))
)

;

CREATE INDEX ix_idempotency_expiry ON api_idempotency_records (expires_at);


CREATE TABLE backup_runs (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	status TEXT NOT NULL,
	database_included BOOLEAN DEFAULT false NOT NULL,
	files_included BOOLEAN DEFAULT false NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	finished_at TIMESTAMP WITH TIME ZONE,
	restore_check_status TEXT DEFAULT 'not_run'::text NOT NULL,
	restore_checked_at TIMESTAMP WITH TIME ZONE,
	error_code TEXT,
	CONSTRAINT backup_runs_pkey PRIMARY KEY (id),
	CONSTRAINT ck_backup_restore_check CHECK (restore_check_status = ANY (ARRAY['not_run'::text, 'passed'::text, 'failed'::text])),
	CONSTRAINT ck_backup_status CHECK (status = ANY (ARRAY['running'::text, 'succeeded'::text, 'failed'::text]))
)

;

CREATE INDEX ix_backup_runs_status_started ON backup_runs (status, started_at);


CREATE TABLE job_runs (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	job_key TEXT NOT NULL,
	job_type TEXT NOT NULL,
	status TEXT NOT NULL,
	attempt_count INTEGER DEFAULT 0 NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE,
	finished_at TIMESTAMP WITH TIME ZONE,
	last_error_code TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT job_runs_pkey PRIMARY KEY (id),
	CONSTRAINT job_runs_job_key_key UNIQUE (job_key),
	CONSTRAINT ck_job_attempts CHECK (attempt_count >= 0),
	CONSTRAINT ck_job_run_status CHECK (status = ANY (ARRAY['queued'::text, 'running'::text, 'succeeded'::text, 'failed'::text, 'cancelled'::text]))
)

;

CREATE INDEX ix_job_runs_status_created ON job_runs (status, created_at);


CREATE TABLE medicines (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	generic_name TEXT NOT NULL,
	brand_name TEXT,
	strength TEXT,
	form TEXT,
	is_sample BOOLEAN DEFAULT true NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT medicines_pkey PRIMARY KEY (id)
)

;

CREATE INDEX ix_medicines_brand_name ON medicines (lower(brand_name));

CREATE INDEX ix_medicines_generic_name ON medicines (lower(generic_name));


CREATE TABLE organizations (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	name TEXT NOT NULL,
	type organization_type NOT NULL,
	registration_ref TEXT,
	status entity_status DEFAULT 'pending'::entity_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT organizations_pkey PRIMARY KEY (id)
)

;

CREATE INDEX ix_organizations_type_status ON organizations (type, status);


CREATE TABLE roles (
	id SMALLSERIAL NOT NULL,
	code TEXT NOT NULL,
	label TEXT NOT NULL,
	CONSTRAINT roles_pkey PRIMARY KEY (id),
	CONSTRAINT roles_code_key UNIQUE (code),
	CONSTRAINT roles_label_key UNIQUE (label),
	CONSTRAINT ck_roles_code CHECK (code = ANY (ARRAY['patient'::text, 'doctor'::text, 'pharmacist'::text, 'lab_staff'::text, 'admin'::text, 'super_admin'::text]))
)

;


CREATE TABLE users (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	firebase_uid TEXT NOT NULL,
	email TEXT,
	display_name TEXT NOT NULL,
	phone TEXT,
	status account_status DEFAULT 'pending'::account_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_firebase_uid_key UNIQUE (firebase_uid)
)

;

CREATE UNIQUE INDEX uq_users_email_ci ON users (lower(email));


CREATE TABLE integration_clients (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	organization_id UUID NOT NULL,
	name TEXT NOT NULL,
	credential_hash TEXT NOT NULL,
	scopes TEXT[] DEFAULT ARRAY[]::text[] NOT NULL,
	status integration_status DEFAULT 'pending'::integration_status NOT NULL,
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_by UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	revoked_at TIMESTAMP WITH TIME ZONE,
	CONSTRAINT integration_clients_pkey PRIMARY KEY (id),
	CONSTRAINT integration_clients_credential_hash_key UNIQUE (credential_hash),
	CONSTRAINT ck_integration_revoked CHECK ((status = 'revoked'::integration_status) = (revoked_at IS NOT NULL)),
	CONSTRAINT ck_integration_scope CHECK (scopes <@ ARRAY['reports:write'::text]),
	CONSTRAINT integration_clients_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT integration_clients_created_by_fkey FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_integration_clients_org_status ON integration_clients (organization_id, status, expires_at);


CREATE TABLE notifications (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	user_id UUID NOT NULL,
	notification_type TEXT NOT NULL,
	title TEXT NOT NULL,
	body TEXT NOT NULL,
	related_type TEXT,
	related_id UUID,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	read_at TIMESTAMP WITH TIME ZONE,
	dedupe_key TEXT NOT NULL,
	CONSTRAINT notifications_pkey PRIMARY KEY (id),
	CONSTRAINT notifications_dedupe_key_key UNIQUE (dedupe_key),
	CONSTRAINT notifications_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_notifications_user_unread ON notifications (user_id, created_at);


CREATE TABLE organization_memberships (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	organization_id UUID NOT NULL,
	user_id UUID NOT NULL,
	role professional_role NOT NULL,
	status verification_status DEFAULT 'pending'::verification_status NOT NULL,
	verified_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT organization_memberships_pkey PRIMARY KEY (id),
	CONSTRAINT uq_membership_org_user_role UNIQUE (organization_id, user_id, role),
	CONSTRAINT organization_memberships_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT organization_memberships_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_memberships_user_status ON organization_memberships (user_id, status);


CREATE TABLE patient_profiles (
	user_id UUID NOT NULL,
	date_of_birth DATE NOT NULL,
	sex TEXT NOT NULL,
	emergency_contact_name TEXT,
	emergency_contact_phone TEXT,
	notification_preferences JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT patient_profiles_pkey PRIMARY KEY (user_id),
	CONSTRAINT ck_patient_sex CHECK (sex IN ('female', 'male', 'intersex', 'another', 'prefer_not_to_say')),
	CONSTRAINT patient_profiles_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;


CREATE TABLE prescription_templates (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	doctor_user_id UUID NOT NULL,
	name TEXT NOT NULL,
	template_type prescription_template_type NOT NULL,
	status prescription_template_status DEFAULT 'active'::prescription_template_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	archived_at TIMESTAMP WITH TIME ZONE,
	CONSTRAINT prescription_templates_pkey PRIMARY KEY (id),
	CONSTRAINT ck_prescription_template_archive CHECK ((status = 'archived'::prescription_template_status) = (archived_at IS NOT NULL)),
	CONSTRAINT ck_prescription_template_name CHECK ((length(btrim(name)) >= 1) AND (length(btrim(name)) <= 120)),
	CONSTRAINT prescription_templates_doctor_user_id_fkey FOREIGN KEY(doctor_user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescription_templates_owner_status ON prescription_templates (doctor_user_id, status, created_at);

CREATE UNIQUE INDEX uq_prescription_template_active_name ON prescription_templates (doctor_user_id, lower(name)) WHERE status = 'active';


CREATE TABLE professional_profiles (
	user_id UUID NOT NULL,
	role professional_role NOT NULL,
	doctor_reference TEXT,
	registration_number TEXT,
	qualifications TEXT,
	specialty TEXT,
	verification_status verification_status DEFAULT 'not_submitted'::verification_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT professional_profiles_pkey PRIMARY KEY (user_id),
	CONSTRAINT professional_profiles_doctor_reference_key UNIQUE (doctor_reference),
	CONSTRAINT ck_doctor_reference_role CHECK ((role = 'doctor'::professional_role) = (doctor_reference IS NOT NULL)),
	CONSTRAINT professional_profiles_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_professional_registration ON professional_profiles (role, registration_number);


CREATE TABLE user_roles (
	user_id UUID NOT NULL,
	role_id SMALLINT NOT NULL,
	assigned_by UUID,
	assigned_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id),
	CONSTRAINT user_roles_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT user_roles_role_id_fkey FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE RESTRICT,
	CONSTRAINT user_roles_assigned_by_fkey FOREIGN KEY(assigned_by) REFERENCES users (id) ON DELETE RESTRICT
)

;


CREATE TABLE verification_applications (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	user_id UUID NOT NULL,
	organization_id UUID,
	role professional_role NOT NULL,
	registration_number TEXT,
	status verification_status DEFAULT 'pending'::verification_status NOT NULL,
	submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	reviewed_by UUID,
	reviewed_at TIMESTAMP WITH TIME ZONE,
	review_reason TEXT,
	CONSTRAINT verification_applications_pkey PRIMARY KEY (id),
	CONSTRAINT ck_verification_review_pair CHECK ((reviewed_by IS NULL) = (reviewed_at IS NULL)),
	CONSTRAINT verification_applications_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT verification_applications_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT verification_applications_reviewed_by_fkey FOREIGN KEY(reviewed_by) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_verification_queue ON verification_applications (status, submitted_at);

CREATE INDEX ix_verification_user ON verification_applications (user_id, submitted_at);


CREATE TABLE access_grants (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	professional_user_id UUID NOT NULL,
	organization_id UUID,
	allow_consultation BOOLEAN DEFAULT false NOT NULL,
	status grant_status DEFAULT 'active'::grant_status NOT NULL,
	starts_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
	revoked_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT access_grants_pkey PRIMARY KEY (id),
	CONSTRAINT ck_grant_revoked CHECK ((status = 'revoked'::grant_status) = (revoked_at IS NOT NULL)),
	CONSTRAINT ck_grant_window CHECK (expires_at > starts_at),
	CONSTRAINT access_grants_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT access_grants_professional_user_id_fkey FOREIGN KEY(professional_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT access_grants_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_grants_patient_status_expiry ON access_grants (patient_user_id, status, expires_at);

CREATE INDEX ix_grants_professional_status_expiry ON access_grants (professional_user_id, status, expires_at);


CREATE TABLE audit_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	actor_user_id UUID,
	actor_client_id UUID,
	action TEXT NOT NULL,
	target_type TEXT NOT NULL,
	target_id UUID,
	outcome TEXT NOT NULL,
	request_id TEXT NOT NULL,
	metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT audit_events_pkey PRIMARY KEY (id),
	CONSTRAINT ck_audit_actor CHECK (num_nonnulls(actor_user_id, actor_client_id) <= 1),
	CONSTRAINT audit_events_actor_user_id_fkey FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT audit_events_actor_client_id_fkey FOREIGN KEY(actor_client_id) REFERENCES integration_clients (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_audit_actor_time ON audit_events (actor_user_id, created_at);

CREATE INDEX ix_audit_request ON audit_events (request_id);

CREATE INDEX ix_audit_target_time ON audit_events (target_type, target_id, created_at);


CREATE TABLE documents (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	owner_user_id UUID NOT NULL,
	patient_user_id UUID,
	uploaded_by UUID,
	source record_source NOT NULL,
	document_type TEXT NOT NULL,
	original_filename TEXT NOT NULL,
	storage_key TEXT NOT NULL,
	media_type TEXT NOT NULL,
	byte_size BIGINT NOT NULL,
	sha256 TEXT,
	status document_status DEFAULT 'active'::document_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	CONSTRAINT documents_pkey PRIMARY KEY (id),
	CONSTRAINT documents_storage_key_key UNIQUE (storage_key),
	CONSTRAINT ck_document_media_type CHECK (media_type = ANY (ARRAY['application/pdf'::text, 'image/jpeg'::text, 'image/png'::text])),
	CONSTRAINT ck_document_sha CHECK ((sha256 IS NULL) OR (sha256 ~ '^[0-9a-fA-F]{64}$'::text)),
	CONSTRAINT ck_document_size CHECK ((byte_size > 0) AND (byte_size <= 10485760)),
	CONSTRAINT documents_owner_user_id_fkey FOREIGN KEY(owner_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT documents_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT documents_uploaded_by_fkey FOREIGN KEY(uploaded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT documents_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES documents (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_documents_owner_date ON documents (owner_user_id, created_at);

CREATE INDEX ix_documents_patient_date ON documents (patient_user_id, created_at);


CREATE TABLE lab_upload_requests (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	laboratory_id UUID NOT NULL,
	request_token_hash TEXT NOT NULL,
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
	status upload_request_status DEFAULT 'active'::upload_request_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	used_at TIMESTAMP WITH TIME ZONE,
	CONSTRAINT lab_upload_requests_pkey PRIMARY KEY (id),
	CONSTRAINT lab_upload_requests_request_token_hash_key UNIQUE (request_token_hash),
	CONSTRAINT lab_upload_requests_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT lab_upload_requests_laboratory_id_fkey FOREIGN KEY(laboratory_id) REFERENCES organizations (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_lab_requests_lab_status_expiry ON lab_upload_requests (laboratory_id, status, expires_at);

CREATE INDEX ix_lab_requests_patient ON lab_upload_requests (patient_user_id, created_at);


CREATE TABLE measurements (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	type measurement_type NOT NULL,
	value NUMERIC(12, 4),
	secondary_value NUMERIC(12, 4),
	unit TEXT NOT NULL,
	measured_at TIMESTAMP WITH TIME ZONE NOT NULL,
	recorded_by UUID NOT NULL,
	source record_source NOT NULL,
	notes TEXT,
	status measurement_status DEFAULT 'active'::measurement_status NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT measurements_pkey PRIMARY KEY (id),
	CONSTRAINT ck_measurement_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT ck_measurement_positive CHECK ((value IS NULL) OR (value > (0)::numeric)),
	CONSTRAINT ck_measurement_secondary_positive CHECK ((secondary_value IS NULL) OR (secondary_value > (0)::numeric)),
	CONSTRAINT ck_measurement_unit CHECK (((type = 'weight'::measurement_type) AND (unit = ANY (ARRAY['kg'::text, 'lb'::text]))) OR ((type = 'blood_glucose'::measurement_type) AND (unit = ANY (ARRAY['mmol/L'::text, 'mg/dL'::text]))) OR ((type = 'blood_pressure'::measurement_type) AND (unit = 'mmHg'::text))),
	CONSTRAINT ck_measurement_values CHECK (((type = 'blood_pressure'::measurement_type) AND (value IS NOT NULL) AND (secondary_value IS NOT NULL) AND (unit = 'mmHg'::text)) OR ((type <> 'blood_pressure'::measurement_type) AND (value IS NOT NULL) AND (secondary_value IS NULL))),
	CONSTRAINT measurements_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT measurements_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT measurements_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES measurements (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_measurements_patient_type_date ON measurements (patient_user_id, type, measured_at);


CREATE TABLE prescription_template_items (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	template_id UUID NOT NULL,
	position SMALLINT NOT NULL,
	medicine_id UUID,
	medicine_name_snapshot TEXT NOT NULL,
	dose_text TEXT NOT NULL,
	route TEXT,
	frequency TEXT NOT NULL,
	duration_days INTEGER,
	instructions TEXT,
	quantity NUMERIC(12, 3),
	quantity_unit TEXT,
	is_prn BOOLEAN DEFAULT false NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT prescription_template_items_pkey PRIMARY KEY (id),
	CONSTRAINT uq_prescription_template_item_position UNIQUE (template_id, position),
	CONSTRAINT ck_prescription_template_item_duration CHECK ((duration_days IS NULL) OR (duration_days > 0)),
	CONSTRAINT ck_prescription_template_item_position CHECK ("position" > 0),
	CONSTRAINT ck_prescription_template_item_quantity CHECK ((quantity IS NULL) OR (quantity > (0)::numeric)),
	CONSTRAINT ck_prescription_template_item_quantity_unit CHECK ((quantity IS NULL) = (quantity_unit IS NULL)),
	CONSTRAINT prescription_template_items_template_id_fkey FOREIGN KEY(template_id) REFERENCES prescription_templates (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_template_items_medicine_id_fkey FOREIGN KEY(medicine_id) REFERENCES medicines (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescription_template_items_template ON prescription_template_items (template_id, position);


CREATE TABLE vaccinations (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	vaccine_name TEXT NOT NULL,
	administered_on DATE NOT NULL,
	dose_details TEXT,
	next_dose_on DATE,
	recorded_by UUID NOT NULL,
	source record_source NOT NULL,
	organization_id UUID,
	notes TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	CONSTRAINT vaccinations_pkey PRIMARY KEY (id),
	CONSTRAINT ck_vaccine_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT ck_vaccine_next_dose CHECK ((next_dose_on IS NULL) OR (next_dose_on >= administered_on)),
	CONSTRAINT uq_vaccinations_replacement UNIQUE (supersedes_id),
	CONSTRAINT vaccinations_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT vaccinations_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT vaccinations_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT vaccinations_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES vaccinations (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_vaccinations_next_dose ON vaccinations (next_dose_on);

CREATE INDEX ix_vaccinations_patient_date ON vaccinations (patient_user_id, administered_on);


CREATE TABLE verification_decisions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	application_id UUID NOT NULL,
	reviewer_user_id UUID NOT NULL,
	decision TEXT NOT NULL,
	reason TEXT NOT NULL,
	decided_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT verification_decisions_pkey PRIMARY KEY (id),
	CONSTRAINT ck_verification_decision CHECK (decision = ANY (ARRAY['approved'::text, 'rejected'::text, 'more_info_requested'::text, 'suspended'::text])),
	CONSTRAINT verification_decisions_application_id_fkey FOREIGN KEY(application_id) REFERENCES verification_applications (id) ON DELETE RESTRICT,
	CONSTRAINT verification_decisions_reviewer_user_id_fkey FOREIGN KEY(reviewer_user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_verification_decisions_history ON verification_decisions (application_id, decided_at);


CREATE TABLE consultations (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	doctor_user_id UUID NOT NULL,
	organization_id UUID,
	grant_id UUID NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	ended_at TIMESTAMP WITH TIME ZONE,
	summary TEXT,
	CONSTRAINT consultations_pkey PRIMARY KEY (id),
	CONSTRAINT ck_consultation_window CHECK ((ended_at IS NULL) OR (ended_at >= started_at)),
	CONSTRAINT consultations_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT consultations_doctor_user_id_fkey FOREIGN KEY(doctor_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT consultations_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT consultations_grant_id_fkey FOREIGN KEY(grant_id) REFERENCES access_grants (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_consultations_doctor_date ON consultations (doctor_user_id, started_at);

CREATE INDEX ix_consultations_patient_date ON consultations (patient_user_id, started_at);


CREATE TABLE grant_categories (
	grant_id UUID NOT NULL,
	category grant_category NOT NULL,
	CONSTRAINT grant_categories_pkey PRIMARY KEY (grant_id, category),
	CONSTRAINT grant_categories_grant_id_fkey FOREIGN KEY(grant_id) REFERENCES access_grants (id) ON DELETE RESTRICT
)

;


CREATE TABLE report_identities (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	laboratory_id UUID NOT NULL,
	lab_reference TEXT NOT NULL,
	initial_upload_request_id UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT report_identities_pkey PRIMARY KEY (id),
	CONSTRAINT report_identities_initial_upload_request_id_key UNIQUE (initial_upload_request_id),
	CONSTRAINT uq_report_identity_lab_reference UNIQUE (laboratory_id, lab_reference),
	CONSTRAINT report_identities_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT report_identities_laboratory_id_fkey FOREIGN KEY(laboratory_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT report_identities_initial_upload_request_id_fkey FOREIGN KEY(initial_upload_request_id) REFERENCES lab_upload_requests (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_report_identities_patient ON report_identities (patient_user_id, created_at);


CREATE TABLE verification_application_documents (
	application_id UUID NOT NULL,
	document_id UUID NOT NULL,
	attached_by UUID NOT NULL,
	attached_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT verification_application_documents_pkey PRIMARY KEY (application_id, document_id),
	CONSTRAINT verification_application_documents_application_id_fkey FOREIGN KEY(application_id) REFERENCES verification_applications (id) ON DELETE RESTRICT,
	CONSTRAINT verification_application_documents_document_id_fkey FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE RESTRICT,
	CONSTRAINT verification_application_documents_attached_by_fkey FOREIGN KEY(attached_by) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_verification_application_documents_document ON verification_application_documents (document_id);


CREATE TABLE allergies (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	consultation_id UUID,
	allergen TEXT NOT NULL,
	reaction TEXT,
	severity TEXT,
	source record_source NOT NULL,
	recorded_by UUID NOT NULL,
	organization_id UUID,
	status clinical_record_status DEFAULT 'active'::clinical_record_status NOT NULL,
	recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	CONSTRAINT allergies_pkey PRIMARY KEY (id),
	CONSTRAINT ck_allergy_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT uq_allergies_replacement UNIQUE (supersedes_id),
	CONSTRAINT allergies_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT allergies_consultation_id_fkey FOREIGN KEY(consultation_id) REFERENCES consultations (id) ON DELETE RESTRICT,
	CONSTRAINT allergies_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT allergies_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT allergies_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES allergies (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_allergies_consultation ON allergies (consultation_id);

CREATE INDEX ix_allergies_patient_date ON allergies (patient_user_id, recorded_at);


CREATE TABLE clinical_notes (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	consultation_id UUID,
	note_type TEXT NOT NULL,
	note_text TEXT NOT NULL,
	source record_source NOT NULL,
	recorded_by UUID NOT NULL,
	organization_id UUID,
	status clinical_record_status DEFAULT 'active'::clinical_record_status NOT NULL,
	recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	CONSTRAINT clinical_notes_pkey PRIMARY KEY (id),
	CONSTRAINT ck_clinical_note_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT uq_clinical_notes_replacement UNIQUE (supersedes_id),
	CONSTRAINT clinical_notes_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT clinical_notes_consultation_id_fkey FOREIGN KEY(consultation_id) REFERENCES consultations (id) ON DELETE RESTRICT,
	CONSTRAINT clinical_notes_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT clinical_notes_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT clinical_notes_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES clinical_notes (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_clinical_notes_consultation ON clinical_notes (consultation_id);

CREATE INDEX ix_clinical_notes_patient_date ON clinical_notes (patient_user_id, recorded_at);


CREATE TABLE conditions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	consultation_id UUID,
	condition_name TEXT NOT NULL,
	clinical_code TEXT,
	description TEXT,
	source record_source NOT NULL,
	recorded_by UUID NOT NULL,
	organization_id UUID,
	status clinical_record_status DEFAULT 'active'::clinical_record_status NOT NULL,
	recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	CONSTRAINT conditions_pkey PRIMARY KEY (id),
	CONSTRAINT ck_condition_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT uq_conditions_replacement UNIQUE (supersedes_id),
	CONSTRAINT conditions_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT conditions_consultation_id_fkey FOREIGN KEY(consultation_id) REFERENCES consultations (id) ON DELETE RESTRICT,
	CONSTRAINT conditions_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT conditions_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT conditions_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES conditions (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_conditions_consultation ON conditions (consultation_id);

CREATE INDEX ix_conditions_patient_date ON conditions (patient_user_id, recorded_at);


CREATE TABLE diagnoses (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	consultation_id UUID,
	diagnosis_name TEXT NOT NULL,
	clinical_code TEXT,
	description TEXT,
	source record_source NOT NULL,
	recorded_by UUID NOT NULL,
	organization_id UUID,
	status clinical_record_status DEFAULT 'active'::clinical_record_status NOT NULL,
	diagnosed_at TIMESTAMP WITH TIME ZONE NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	CONSTRAINT diagnoses_pkey PRIMARY KEY (id),
	CONSTRAINT ck_diagnosis_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT uq_diagnoses_replacement UNIQUE (supersedes_id),
	CONSTRAINT diagnoses_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT diagnoses_consultation_id_fkey FOREIGN KEY(consultation_id) REFERENCES consultations (id) ON DELETE RESTRICT,
	CONSTRAINT diagnoses_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT diagnoses_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT diagnoses_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES diagnoses (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_diagnoses_consultation ON diagnoses (consultation_id);

CREATE INDEX ix_diagnoses_patient_date ON diagnoses (patient_user_id, diagnosed_at);


CREATE TABLE prescriptions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	consultation_id UUID,
	prescriber_user_id UUID,
	source prescription_source NOT NULL,
	claimed_prescriber TEXT,
	review_status prescription_review_status DEFAULT 'not_reviewed'::prescription_review_status NOT NULL,
	reviewed_by UUID,
	reviewed_at TIMESTAMP WITH TIME ZONE,
	status prescription_status DEFAULT 'draft'::prescription_status NOT NULL,
	issued_at TIMESTAMP WITH TIME ZONE,
	starts_on DATE,
	ends_on DATE,
	previous_prescription_id UUID,
	original_document_id UUID,
	created_by UUID NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	version INTEGER DEFAULT 1 NOT NULL,
	status_reason TEXT,
	CONSTRAINT prescriptions_pkey PRIMARY KEY (id),
	CONSTRAINT ck_prescription_dates CHECK ((ends_on IS NULL) OR (starts_on IS NULL) OR (ends_on >= starts_on)),
	CONSTRAINT ck_prescription_issue_time CHECK ((status <> ALL (ARRAY['active'::prescription_status, 'completed'::prescription_status, 'discontinued'::prescription_status, 'cancelled'::prescription_status, 'superseded'::prescription_status])) OR (issued_at IS NOT NULL)),
	CONSTRAINT ck_prescription_issuer CHECK ((source <> 'doctor'::prescription_source) OR (prescriber_user_id IS NOT NULL)),
	CONSTRAINT ck_prescription_review_pair CHECK ((reviewed_by IS NULL) = (reviewed_at IS NULL)),
	CONSTRAINT prescriptions_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT prescriptions_consultation_id_fkey FOREIGN KEY(consultation_id) REFERENCES consultations (id) ON DELETE RESTRICT,
	CONSTRAINT prescriptions_prescriber_user_id_fkey FOREIGN KEY(prescriber_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT prescriptions_reviewed_by_fkey FOREIGN KEY(reviewed_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT prescriptions_previous_prescription_id_fkey FOREIGN KEY(previous_prescription_id) REFERENCES prescriptions (id) ON DELETE RESTRICT,
	CONSTRAINT prescriptions_original_document_id_fkey FOREIGN KEY(original_document_id) REFERENCES documents (id) ON DELETE RESTRICT,
	CONSTRAINT prescriptions_created_by_fkey FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescriptions_patient_status ON prescriptions (patient_user_id, status, created_at);

CREATE INDEX ix_prescriptions_prescriber ON prescriptions (prescriber_user_id, created_at);


CREATE TABLE reports (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	laboratory_id UUID,
	report_identity_id UUID,
	upload_request_id UUID,
	document_id UUID NOT NULL,
	report_type TEXT NOT NULL,
	report_date DATE,
	notes TEXT,
	source record_source NOT NULL,
	uploaded_by UUID,
	status report_status DEFAULT 'active'::report_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	supersedes_id UUID,
	correction_reason TEXT,
	CONSTRAINT reports_pkey PRIMARY KEY (id),
	CONSTRAINT ck_report_correction CHECK ((supersedes_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT uq_reports_replacement UNIQUE (supersedes_id),
	CONSTRAINT reports_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT reports_laboratory_id_fkey FOREIGN KEY(laboratory_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT reports_report_identity_id_fkey FOREIGN KEY(report_identity_id) REFERENCES report_identities (id) ON DELETE RESTRICT,
	CONSTRAINT reports_upload_request_id_fkey FOREIGN KEY(upload_request_id) REFERENCES lab_upload_requests (id) ON DELETE RESTRICT,
	CONSTRAINT reports_document_id_fkey FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE RESTRICT,
	CONSTRAINT reports_uploaded_by_fkey FOREIGN KEY(uploaded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT reports_supersedes_id_fkey FOREIGN KEY(supersedes_id) REFERENCES reports (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_reports_identity_date ON reports (report_identity_id, report_date);

CREATE INDEX ix_reports_lab_date ON reports (laboratory_id, report_date);

CREATE INDEX ix_reports_patient_date ON reports (patient_user_id, report_date);


CREATE TABLE integration_submissions (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	client_id UUID NOT NULL,
	upload_request_id UUID NOT NULL,
	external_report_id TEXT NOT NULL,
	idempotency_key TEXT NOT NULL,
	status submission_status DEFAULT 'received'::submission_status NOT NULL,
	report_id UUID,
	received_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	error_code TEXT,
	CONSTRAINT integration_submissions_pkey PRIMARY KEY (id),
	CONSTRAINT uq_integration_idempotency UNIQUE (client_id, idempotency_key),
	CONSTRAINT integration_submissions_client_id_fkey FOREIGN KEY(client_id) REFERENCES integration_clients (id) ON DELETE RESTRICT,
	CONSTRAINT integration_submissions_upload_request_id_fkey FOREIGN KEY(upload_request_id) REFERENCES lab_upload_requests (id) ON DELETE RESTRICT,
	CONSTRAINT integration_submissions_report_id_fkey FOREIGN KEY(report_id) REFERENCES reports (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_integration_submissions_status ON integration_submissions (status, received_at);

CREATE UNIQUE INDEX uq_integration_external_report ON integration_submissions (client_id, external_report_id);


CREATE TABLE prescription_items (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	prescription_id UUID NOT NULL,
	medicine_id UUID,
	medicine_name_snapshot TEXT NOT NULL,
	dose_text TEXT NOT NULL,
	route TEXT,
	frequency TEXT NOT NULL,
	duration_days INTEGER,
	instructions TEXT,
	quantity NUMERIC(12, 3),
	quantity_unit TEXT,
	is_prn BOOLEAN DEFAULT false NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT prescription_items_pkey PRIMARY KEY (id),
	CONSTRAINT ck_item_duration CHECK ((duration_days IS NULL) OR (duration_days > 0)),
	CONSTRAINT ck_item_quantity CHECK ((quantity IS NULL) OR (quantity > (0)::numeric)),
	CONSTRAINT ck_item_quantity_unit CHECK ((quantity IS NULL) = (quantity_unit IS NULL)),
	CONSTRAINT prescription_items_prescription_id_fkey FOREIGN KEY(prescription_id) REFERENCES prescriptions (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_items_medicine_id_fkey FOREIGN KEY(medicine_id) REFERENCES medicines (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescription_items_prescription ON prescription_items (prescription_id);


CREATE TABLE prescription_ocr_jobs (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	patient_user_id UUID NOT NULL,
	original_document_id UUID NOT NULL,
	requested_by_user_id UUID NOT NULL,
	status prescription_ocr_job_status DEFAULT 'queued'::prescription_ocr_job_status NOT NULL,
	extracted_fields JSONB,
	attempt_count INTEGER DEFAULT 0 NOT NULL,
	error_code TEXT,
	resulting_prescription_id UUID,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT prescription_ocr_jobs_pkey PRIMARY KEY (id),
	CONSTRAINT prescription_ocr_jobs_resulting_prescription_id_key UNIQUE (resulting_prescription_id),
	CONSTRAINT uq_prescription_ocr_patient_document UNIQUE (patient_user_id, original_document_id),
	CONSTRAINT ck_prescription_ocr_attempts CHECK (attempt_count >= 0),
	CONSTRAINT ck_prescription_ocr_draft_state CHECK ((resulting_prescription_id IS NULL) = (status <> 'draft_created'::prescription_ocr_job_status)),
	CONSTRAINT ck_prescription_ocr_extracted_object CHECK ((extracted_fields IS NULL) OR (jsonb_typeof(extracted_fields) = 'object'::text)),
	CONSTRAINT prescription_ocr_jobs_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT prescription_ocr_jobs_original_document_id_fkey FOREIGN KEY(original_document_id) REFERENCES documents (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_ocr_jobs_requested_by_user_id_fkey FOREIGN KEY(requested_by_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_ocr_jobs_resulting_prescription_id_fkey FOREIGN KEY(resulting_prescription_id) REFERENCES prescriptions (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescription_ocr_patient_created ON prescription_ocr_jobs (patient_user_id, created_at);

CREATE INDEX ix_prescription_ocr_status_created ON prescription_ocr_jobs (status, created_at);


CREATE TABLE prescription_reviews (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	prescription_id UUID NOT NULL,
	reviewer_user_id UUID NOT NULL,
	outcome review_outcome NOT NULL,
	notes TEXT,
	reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT prescription_reviews_pkey PRIMARY KEY (id),
	CONSTRAINT prescription_reviews_prescription_id_fkey FOREIGN KEY(prescription_id) REFERENCES prescriptions (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_reviews_reviewer_user_id_fkey FOREIGN KEY(reviewer_user_id) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescription_reviews_history ON prescription_reviews (prescription_id, reviewed_at);


CREATE TABLE prescription_shares (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	prescription_id UUID NOT NULL,
	patient_user_id UUID NOT NULL,
	claim_token_hash TEXT NOT NULL,
	status share_status DEFAULT 'created'::share_status NOT NULL,
	claim_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
	claimed_by UUID,
	claimed_organization_id UUID,
	claimed_at TIMESTAMP WITH TIME ZONE,
	confirmed_at TIMESTAMP WITH TIME ZONE,
	confirmed_access_expires_at TIMESTAMP WITH TIME ZONE,
	revoked_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT prescription_shares_pkey PRIMARY KEY (id),
	CONSTRAINT prescription_shares_claim_token_hash_key UNIQUE (claim_token_hash),
	CONSTRAINT ck_share_claim_pair CHECK ((claimed_by IS NULL) = (claimed_at IS NULL)),
	CONSTRAINT ck_share_access_expiry CHECK ((confirmed_at IS NULL) = (confirmed_access_expires_at IS NULL)),
	CONSTRAINT ck_share_revoked CHECK ((status = 'revoked'::share_status) = (revoked_at IS NOT NULL)),
	CONSTRAINT ck_share_confirm CHECK ((status <> 'confirmed'::share_status) OR ((confirmed_at IS NOT NULL) AND (claimed_by IS NOT NULL))),
	CONSTRAINT ck_share_claim_org CHECK ((claimed_by IS NULL) = (claimed_organization_id IS NULL)),
	CONSTRAINT prescription_shares_prescription_id_fkey FOREIGN KEY(prescription_id) REFERENCES prescriptions (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_shares_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT,
	CONSTRAINT prescription_shares_claimed_by_fkey FOREIGN KEY(claimed_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT prescription_shares_claimed_organization_id_fkey FOREIGN KEY(claimed_organization_id) REFERENCES organizations (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_prescription_shares_expiry ON prescription_shares (status, claim_expires_at, confirmed_access_expires_at);


CREATE TABLE record_corrections (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	condition_id UUID,
	diagnosis_id UUID,
	allergy_id UUID,
	clinical_note_id UUID,
	requested_by UUID NOT NULL,
	reason TEXT NOT NULL,
	request_status TEXT DEFAULT 'open'::text NOT NULL,
	reviewed_by UUID,
	reviewed_at TIMESTAMP WITH TIME ZONE,
	resolution_reason TEXT,
	replacement_record_type TEXT,
	replacement_record_id UUID,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT record_corrections_pkey PRIMARY KEY (id),
	CONSTRAINT ck_correction_one_target CHECK (num_nonnulls(condition_id, diagnosis_id, allergy_id, clinical_note_id) = 1),
	CONSTRAINT ck_correction_replacement_pair CHECK ((replacement_record_type IS NULL) = (replacement_record_id IS NULL)),
	CONSTRAINT ck_correction_status CHECK (request_status = ANY (ARRAY['open'::text, 'accepted'::text, 'rejected'::text, 'resolved'::text])),
	CONSTRAINT record_corrections_condition_id_fkey FOREIGN KEY(condition_id) REFERENCES conditions (id) ON DELETE RESTRICT,
	CONSTRAINT record_corrections_diagnosis_id_fkey FOREIGN KEY(diagnosis_id) REFERENCES diagnoses (id) ON DELETE RESTRICT,
	CONSTRAINT record_corrections_allergy_id_fkey FOREIGN KEY(allergy_id) REFERENCES allergies (id) ON DELETE RESTRICT,
	CONSTRAINT record_corrections_clinical_note_id_fkey FOREIGN KEY(clinical_note_id) REFERENCES clinical_notes (id) ON DELETE RESTRICT,
	CONSTRAINT record_corrections_requested_by_fkey FOREIGN KEY(requested_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT record_corrections_reviewed_by_fkey FOREIGN KEY(reviewed_by) REFERENCES users (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_corrections_allergy ON record_corrections (allergy_id, created_at);

CREATE INDEX ix_corrections_condition ON record_corrections (condition_id, created_at);

CREATE INDEX ix_corrections_diagnosis ON record_corrections (diagnosis_id, created_at);

CREATE INDEX ix_corrections_note ON record_corrections (clinical_note_id, created_at);


CREATE TABLE dispensing_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	prescription_id UUID NOT NULL,
	pharmacist_user_id UUID NOT NULL,
	organization_id UUID NOT NULL,
	share_id UUID,
	dispensed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	request_key TEXT NOT NULL,
	notes TEXT,
	reversal_of_id UUID,
	reason TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT dispensing_events_pkey PRIMARY KEY (id),
	CONSTRAINT dispensing_events_request_key_key UNIQUE (request_key),
	CONSTRAINT uq_dispensing_single_reversal UNIQUE (reversal_of_id),
	CONSTRAINT ck_dispensing_reversal CHECK ((reversal_of_id IS NULL) = (reason IS NULL)),
	CONSTRAINT dispensing_events_prescription_id_fkey FOREIGN KEY(prescription_id) REFERENCES prescriptions (id) ON DELETE RESTRICT,
	CONSTRAINT dispensing_events_pharmacist_user_id_fkey FOREIGN KEY(pharmacist_user_id) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT dispensing_events_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE RESTRICT,
	CONSTRAINT dispensing_events_share_id_fkey FOREIGN KEY(share_id) REFERENCES prescription_shares (id) ON DELETE RESTRICT,
	CONSTRAINT dispensing_events_reversal_of_id_fkey FOREIGN KEY(reversal_of_id) REFERENCES dispensing_events (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_dispensing_pharmacist_date ON dispensing_events (pharmacist_user_id, dispensed_at);

CREATE INDEX ix_dispensing_prescription_date ON dispensing_events (prescription_id, dispensed_at);


CREATE TABLE medication_schedules (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	prescription_item_id UUID NOT NULL,
	patient_user_id UUID NOT NULL,
	timezone TEXT NOT NULL,
	starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
	ends_at TIMESTAMP WITH TIME ZONE,
	confirmed_at TIMESTAMP WITH TIME ZONE NOT NULL,
	status schedule_status DEFAULT 'active'::schedule_status NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	version INTEGER DEFAULT 1 NOT NULL,
	CONSTRAINT medication_schedules_pkey PRIMARY KEY (id),
	CONSTRAINT ck_schedule_window CHECK ((ends_at IS NULL) OR (ends_at >= starts_at)),
	CONSTRAINT medication_schedules_prescription_item_id_fkey FOREIGN KEY(prescription_item_id) REFERENCES prescription_items (id) ON DELETE RESTRICT,
	CONSTRAINT medication_schedules_patient_user_id_fkey FOREIGN KEY(patient_user_id) REFERENCES patient_profiles (user_id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_schedules_item ON medication_schedules (prescription_item_id);

CREATE INDEX ix_schedules_patient_status ON medication_schedules (patient_user_id, status, starts_at);

CREATE UNIQUE INDEX uq_active_item_schedule ON medication_schedules (prescription_item_id) WHERE status IN ('active', 'paused');


CREATE TABLE dispensing_items (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	event_id UUID NOT NULL,
	prescription_item_id UUID NOT NULL,
	quantity NUMERIC(12, 3) NOT NULL,
	quantity_unit TEXT NOT NULL,
	CONSTRAINT dispensing_items_pkey PRIMARY KEY (id),
	CONSTRAINT uq_dispensing_event_item UNIQUE (event_id, prescription_item_id),
	CONSTRAINT ck_dispensing_quantity CHECK (quantity > (0)::numeric),
	CONSTRAINT dispensing_items_event_id_fkey FOREIGN KEY(event_id) REFERENCES dispensing_events (id) ON DELETE RESTRICT,
	CONSTRAINT dispensing_items_prescription_item_id_fkey FOREIGN KEY(prescription_item_id) REFERENCES prescription_items (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_dispensing_items_item ON dispensing_items (prescription_item_id);


CREATE TABLE dose_occurrences (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	schedule_id UUID NOT NULL,
	scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
	status dose_status DEFAULT 'upcoming'::dose_status NOT NULL,
	snoozed_until TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	CONSTRAINT dose_occurrences_pkey PRIMARY KEY (id),
	CONSTRAINT uq_dose_occurrence UNIQUE (schedule_id, scheduled_for),
	CONSTRAINT dose_occurrences_schedule_id_fkey FOREIGN KEY(schedule_id) REFERENCES medication_schedules (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_dose_occurrences_due ON dose_occurrences (status, scheduled_for);

CREATE INDEX ix_dose_occurrences_schedule ON dose_occurrences (schedule_id, scheduled_for);


CREATE TABLE schedule_times (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	schedule_id UUID NOT NULL,
	time_of_day TIME WITHOUT TIME ZONE NOT NULL,
	CONSTRAINT schedule_times_pkey PRIMARY KEY (id),
	CONSTRAINT uq_schedule_time UNIQUE (schedule_id, time_of_day),
	CONSTRAINT schedule_times_schedule_id_fkey FOREIGN KEY(schedule_id) REFERENCES medication_schedules (id) ON DELETE RESTRICT
)

;


CREATE TABLE medication_logs (
	id UUID DEFAULT gen_random_uuid() NOT NULL,
	dose_occurrence_id UUID NOT NULL,
	response dose_response NOT NULL,
	reported_taken_at TIMESTAMP WITH TIME ZONE,
	recorded_by UUID NOT NULL,
	recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
	correction_of_id UUID,
	correction_reason TEXT,
	CONSTRAINT medication_logs_pkey PRIMARY KEY (id),
	CONSTRAINT ck_medication_log_correction CHECK ((correction_of_id IS NULL) = (correction_reason IS NULL)),
	CONSTRAINT ck_medication_log_taken_time CHECK ((response <> 'taken'::dose_response) OR (reported_taken_at IS NOT NULL)),
	CONSTRAINT uq_log_single_correction UNIQUE (correction_of_id),
	CONSTRAINT medication_logs_dose_occurrence_id_fkey FOREIGN KEY(dose_occurrence_id) REFERENCES dose_occurrences (id) ON DELETE RESTRICT,
	CONSTRAINT medication_logs_recorded_by_fkey FOREIGN KEY(recorded_by) REFERENCES users (id) ON DELETE RESTRICT,
	CONSTRAINT medication_logs_correction_of_id_fkey FOREIGN KEY(correction_of_id) REFERENCES medication_logs (id) ON DELETE RESTRICT
)

;

CREATE INDEX ix_medication_logs_occurrence ON medication_logs (dose_occurrence_id, recorded_at);

CREATE UNIQUE INDEX uq_log_initial_response ON medication_logs (dose_occurrence_id) WHERE correction_of_id IS NULL;

INSERT INTO roles (code, label) VALUES ('patient','Patient'),('doctor','Doctor'),('pharmacist','Pharmacist'),('lab_staff','Laboratory staff'),('admin','Administrator'),('super_admin','Super Administrator');
