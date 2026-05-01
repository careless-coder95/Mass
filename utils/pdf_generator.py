from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_accounts_pdf(accounts, file_path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)
    
    content = []
    
    content.append(Paragraph("Telegram Accounts Backup", styles['Title']))
    content.append(Spacer(1, 15))
    
    for i, acc in enumerate(accounts, start=1):
        text = f"""
        <b>Account {i}</b><br/>
        Phone: {acc['phone']}<br/>
        Password: {acc['password'] if acc['password'] else 'Not Set'}<br/>
        Session: {acc['session_string'][:50]}...<br/>
        Added: {acc['created_at'][:10]}<br/><br/>
        """
        
        content.append(Paragraph(text, styles['Normal']))
        content.append(Spacer(1, 10))
    
    doc.build(content)
