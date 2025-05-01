from io import BytesIO
from datetime import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generate_pdf(calculation):
    """Generate a PDF from calculation data."""
    try:
        # Get profile and calculation data
        profile = calculation.profile
        inputs = json.loads(calculation.input_data)
        results = json.loads(calculation.result_data)
        
        # Create buffer for PDF file
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Initialize story array for elements
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Create custom styles
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading3'],
            spaceAfter=6,
            spaceBefore=12
        )
        
        # Add title
        story.append(Paragraph(f"Bulletin de Paie - {profile.name}", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Add calculation date
        date_str = calculation.calculation_date.strftime("%d/%m/%Y à %H:%M")
        story.append(Paragraph(f"Calculé le: {date_str}", normal_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Add profile info table
        profile_data = [
            ["Informations du Profil", ""],
            ["Nom", profile.name],
            ["Taux horaire", f"{profile.hourly_rate:.2f} DH/h"],
            ["Prime de fonction", f"{profile.function_bonus_base_amount:.2f} DH"],
            ["Prime de performance", f"{profile.performance_bonus_amount:.2f} DH"],
            ["Prime de niveau", f"{profile.prime_de_niveau_amount:.2f} DH"],
            ["Taux d'ancienneté", f"{profile.seniority_rate_percent:.1f}%"]
        ]
        
        profile_table = Table(profile_data, colWidths=[doc.width/2.0]*2)
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        story.append(profile_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Add inputs table
        story.append(Paragraph("Données d'entrée", section_title_style))
        
        input_data = [
            ["Paramètre", "Valeur"],
            ["Heures travaillées", f"{inputs['worked_hours']:.2f} h"],
            ["Heures de nuit", f"{inputs['night_hours_worked']:.2f} h"],
            ["Heures supp. (125%)", f"{inputs['extra_hours_125']:.2f} h"],
            ["Heures supp. (150%)", f"{inputs['extra_hours_150']:.2f} h"],
            ["Heures supp. (200%)", f"{inputs['extra_hours_200']:.2f} h"],
            ["Jours congés payés", f"{inputs['paid_leave_days']:.1f} j"],
            ["Jours congés except.", f"{inputs['exceptional_leave_days']:.1f} j"],
        ]
        
        input_table = Table(input_data, colWidths=[doc.width/2.0]*2)
        input_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        story.append(input_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Add earnings table
        story.append(Paragraph("Revenus", section_title_style))
        
        earnings_data = [["Composante", "Montant (DH)"]]
        for key, value in results['earnings'].items():
            if value > 0:
                earnings_data.append([key, f"{value:.2f}"])
        
        earnings_table = Table(earnings_data, colWidths=[doc.width/2.0]*2)
        earnings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        story.append(earnings_table)
        
        # Add total gross salary
        gross_data = [["Salaire Brut", f"{results['gross_salary']:.2f} DH"]]
        gross_table = Table(gross_data, colWidths=[doc.width/2.0]*2)
        gross_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('GRID', (0, 0), (1, 0), 0.5, colors.grey),
        ]))
        story.append(gross_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Add deductions table
        story.append(Paragraph("Cotisations Sociales", section_title_style))
        
        deductions_data = [["Cotisation", "Montant (DH)"]]
        for key, value in results['social_pension_contributions'].items():
            deductions_data.append([key, f"{value:.2f}"])
        
        deductions_table = Table(deductions_data, colWidths=[doc.width/2.0]*2)
        deductions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        story.append(deductions_table)
        
        # Add social contributions total
        social_total_data = [["Total des cotisations sociales", f"{results['total_social_pension_contributions']:.2f} DH"]]
        social_total_table = Table(social_total_data, colWidths=[doc.width/2.0]*2)
        social_total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightpink),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 6),
            ('GRID', (0, 0), (1, 0), 0.5, colors.grey),
        ]))
        story.append(social_total_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Add IGR section
        story.append(Paragraph("Impôt sur le Revenu (IR)", section_title_style))
        
        igr_data = [
            ["Revenu imposable (SNI)", f"{results['igr_calculation_details']['Net Taxable Income (SNI - Monthly)']:.2f} DH"],
            ["Impôt sur le revenu (IR)", f"{results['igr_calculation_details']['IGR (Income Tax - calc. 0 dependents)']:.2f} DH"]
        ]
        
        igr_table = Table(igr_data, colWidths=[doc.width/2.0]*2)
        igr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(igr_table)
        story.append(Spacer(1, 0.7*cm))
        
        # Add final summary table
        story.append(Paragraph("Récapitulatif", heading_style))
        
        summary_data = [
            ["Salaire Brut", f"{results['gross_salary']:.2f} DH"],
            ["Total Cotisations Sociales", f"-{results['total_social_pension_contributions']:.2f} DH"],
            ["Impôt sur le Revenu", f"-{results['igr_calculation_details']['IGR (Income Tax - calc. 0 dependents)']:.2f} DH"],
            ["Salaire Net", f"{results['net_salary']:.2f} DH"]
        ]
        
        summary_table = Table(summary_data, colWidths=[doc.width/2.0]*2)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 2), colors.white),
            ('BACKGROUND', (0, 3), (1, 3), colors.lightblue),
            ('TEXTCOLOR', (0, 3), (1, 3), colors.black),
            ('FONTNAME', (0, 3), (1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (1, 3), 12),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 3), (1, 3), 6),
            ('TOPPADDING', (0, 3), (1, 3), 6),
        ]))
        story.append(summary_table)
        
        # Add footer
        footer_text = """
        Document généré automatiquement par l'application Bulletin de Paie.
        Ce document est informatif et ne constitue pas un bulletin de paie officiel.
        """
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF document
        doc.build(story)
        
        # Get PDF from buffer
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None 