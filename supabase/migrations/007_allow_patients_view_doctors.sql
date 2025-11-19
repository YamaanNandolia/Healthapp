-- Allow patients to view their assigned doctor's information
-- This fixes the issue where patient dashboard shows empty doctor info

-- Add policy: Patients can view their assigned doctor
CREATE POLICY "Patients can view their assigned doctor"
  ON public.doctor
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 
      FROM public.patient 
      WHERE patient.doctor_id = doctor.id 
      AND patient.id = auth.uid()
    )
  );

COMMENT ON POLICY "Patients can view their assigned doctor" ON public.doctor IS 
  'Allows patients to view information about the doctor assigned to them';

