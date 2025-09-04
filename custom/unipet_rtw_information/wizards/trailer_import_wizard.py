# File: custom/unipet_rtw_information/wizards/trailer_import_wizard.py

import base64
import csv
import json
import io
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TrailerImportWizard(models.TransientModel):
    _name = 'rtw_information.trailer.import.wizard'
    _description = 'Import Trailers from CSV'

    import_file = fields.Binary(
        string="CSV File",
        required=True,
        help="Upload a CSV file with trailer data"
    )
    file_name = fields.Char(string="File Name")
    
    import_mode = fields.Selection([
        ('create_only', 'Create New Records Only'),
        ('update_existing', 'Update Existing Records'),
        ('create_update', 'Create New and Update Existing')
    ], default='create_only', required=True)
    
    sample_data = fields.Text(
        string="Sample CSV Format",
        readonly=True,
        default="""license_plate,is_rigid,manufacturer,contractor,compartment_capacities
TRL001,True,Volvo,sktl,"[25000, 30000, 25000]"
TRL002,False,Mercedes,ldst,"[40000, 35000]"
TRL003,True,Scania,crb,"[20000, 20000, 20000, 15000]"

Instructions:
- license_plate: Unique identifier for the trailer
- is_rigid: True or False
- manufacturer: Trailer manufacturer name
- contractor: sktl, ldst, or crb
- compartment_capacities: JSON array of compartment capacities [capacity1, capacity2, ...]"""
    )

    def action_import_trailers(self):
        """Import trailers from uploaded CSV file"""
        if not self.import_file:
            raise UserError(_("Please upload a CSV file"))

        try:
            # Decode the uploaded file
            file_data = base64.b64decode(self.import_file)
            file_content = file_data.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            imported_count = 0
            updated_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                try:
                    result = self._process_trailer_row(row, row_num)
                    if result['action'] == 'created':
                        imported_count += 1
                    elif result['action'] == 'updated':
                        updated_count += 1
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Prepare result message
            message_parts = []
            if imported_count > 0:
                message_parts.append(f"{imported_count} trailers created")
            if updated_count > 0:
                message_parts.append(f"{updated_count} trailers updated")
            if error_count > 0:
                message_parts.append(f"{error_count} errors occurred")
            
            message = "Import completed: " + ", ".join(message_parts)
            
            if errors:
                message += "\n\nErrors:\n" + "\n".join(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    message += f"\n... and {len(errors) - 10} more errors"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success' if error_count == 0 else 'warning',
                    'message': message,
                    'sticky': True,
                }
            }
            
        except Exception as e:
            raise UserError(_("Error processing file: %s") % str(e))

    def _process_trailer_row(self, row, row_num):
        """Process a single trailer row from CSV"""
        license_plate = row.get('license_plate')
        if license_plate is None or not license_plate.strip():
            raise ValidationError(f"Row {row_num}: License plate is required")
        license_plate = license_plate.strip()

        # Handle manufacturer empty strings
        manufacturer = row.get('manufacturer') or ''
        manufacturer = manufacturer.strip()

        # Handle contractor
        contractor = row.get('contractor') or ''
        contractor = contractor.strip()

        # Parse boolean fields safely
        is_rigid = str(row.get('is_rigid', 'True')).strip().lower() == 'true'

        # Parse compartment capacities and strip extra quotes
        compartment_capacities_str = row.get('compartment_capacities', '[]').strip()
        # Remove wrapping quotes if any
        if compartment_capacities_str.startswith('"') and compartment_capacities_str.endswith('"'):
            compartment_capacities_str = compartment_capacities_str[1:-1]

        try:
            compartment_capacities = json.loads(compartment_capacities_str)
            if not isinstance(compartment_capacities, list):
                raise ValueError("Compartment capacities must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValidationError(f"Row {row_num}: Invalid compartment_capacities format: {str(e)}")

        trailer_vals = {
            'name': license_plate,
            'manufacturer': manufacturer,
            'contractor': contractor or False,
            'is_rigid': is_rigid,
        }

        # Validate contractor selection
        if contractor:
            valid_contractors = dict(self.env['rtw_information.trailer']._fields['contractor'].selection)
            if contractor not in valid_contractors:
                raise ValidationError(f"Row {row_num}: Invalid contractor '{contractor}'. Valid options: {list(valid_contractors.keys())}")

        # Check existing trailer
        existing_trailer = self.env['rtw_information.trailer'].search([('name', '=', license_plate)], limit=1)
        if existing_trailer:
            if self.import_mode == 'create_only':
                raise ValidationError(f"Row {row_num}: Trailer '{license_plate}' already exists")
            elif self.import_mode in ('update_existing', 'create_update'):
                return self._update_trailer(existing_trailer, trailer_vals, compartment_capacities)
        else:
            if self.import_mode == 'update_existing':
                raise ValidationError(f"Row {row_num}: Trailer '{license_plate}' does not exist for update")
            else:
                return self._create_trailer(trailer_vals, compartment_capacities)

    def _create_trailer(self, trailer_vals, compartment_capacities):
        """Create a new trailer with compartments"""
        # Prepare compartment data
        compartment_commands = []
        for capacity in compartment_capacities:
            compartment_commands.append((0, 0, {
                'capacity': float(capacity),
                'quantity': 0.0,
            }))
        
        trailer_vals['compartments'] = compartment_commands
        
        # Create trailer
        trailer = self.env['rtw_information.trailer'].create(trailer_vals)
        
        return {
            'action': 'created',
            'trailer_id': trailer.id,
            'trailer_name': trailer.name
        }

    def _update_trailer(self, trailer, trailer_vals, compartment_capacities):
        """Update existing trailer and its compartments safely"""
        # Update trailer fields (excluding compartments)
        trailer_update_vals = {k: v for k, v in trailer_vals.items() if k != 'compartments'}
        trailer.write(trailer_update_vals)

        existing_compartments = trailer.compartments.sorted('id')
        num_existing = len(existing_compartments)
        num_new = len(compartment_capacities)

        # Update existing compartments
        for idx, capacity in enumerate(compartment_capacities):
            if idx < num_existing:
                existing_compartments[idx].write({
                    'capacity': float(capacity),
                    # Optionally update 'quantity' or other fields if needed
                })
            else:
                # Add new compartment
                trailer.compartments = [(0, 0, {
                    'capacity': float(capacity),
                    'quantity': 0.0,
                })]

        # Remove extra compartments if any
        if num_existing > num_new:
            compartments_to_remove = existing_compartments[num_new:]
            compartments_to_remove.unlink()

        return {
            'action': 'updated',
            'trailer_id': trailer.id,
            'trailer_name': trailer.name
        }

    def action_download_sample(self):
        self.ensure_one()  # make sure the wizard record exists

        # CSV content
        sample_csv_content = """license_plate,is_rigid,manufacturer,contractor,compartment_capacities
    TRL001,True,Volvo,sktl,"[25000, 30000, 25000]"
    TRL002,False,Mercedes,ldst,"[40000, 35000]"
    TRL003,True,Scania,crb,"[20000, 20000, 20000, 15000]"
    """

        # Create attachment linked to current user
        attachment = self.env['ir.attachment'].create({
            'name': 'trailer_import_sample.csv',
            'type': 'binary',
            'datas': base64.b64encode(sample_csv_content.encode('utf-8')),
            'res_model': 'res.users',
            'res_id': self.env.user.id,
            'mimetype': 'text/csv',
        })

        # Return download URL
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',  # open in new tab for download
        }
