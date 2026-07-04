export type PortalSignupRole = 'student' | 'staff' | 'admin';
export type PortalAuthMode = 'register' | 'login';

const SUPPORT_MESSAGE = 'Please allow pop-ups for this site to use this action.';

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function goToPortalSignup(role: PortalSignupRole, mode: PortalAuthMode = 'register'): void {
  const params = new URLSearchParams({ role });
  if (mode !== 'register') {
    params.set('mode', mode);
  }
  window.location.assign(`signup.html?${params.toString()}`);
}

export function goToPage(path: string): void {
  window.location.assign(path);
}

export function openExternalPage(url: string): void {
  window.open(url, '_blank', 'noopener,noreferrer');
}

export function downloadTextFile(filename: string, content: string): void {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function printHtmlReport(title: string, sections: Array<{ heading: string; rows: string[] }>): void {
  const popup = window.open('', '_blank', 'noopener,noreferrer');

  if (!popup) {
    window.alert(SUPPORT_MESSAGE);
    return;
  }

  const renderedSections = sections
    .map(
      (section) => `
        <section style="margin-bottom: 24px;">
          <h2 style="font-size: 18px; margin-bottom: 12px;">${escapeHtml(section.heading)}</h2>
          <ul style="padding-left: 18px; margin: 0;">
            ${section.rows.map((row) => `<li style="margin-bottom: 8px;">${escapeHtml(row)}</li>`).join('')}
          </ul>
        </section>
      `
    )
    .join('');

  popup.document.write(`
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>${escapeHtml(title)}</title>
      </head>
      <body style="font-family: Inter, Arial, sans-serif; color: #0B1D35; margin: 32px;">
        <h1 style="margin-bottom: 8px;">${escapeHtml(title)}</h1>
        <p style="margin-top: 0; margin-bottom: 24px;">Generated from the Texas CNA Academy portal on ${new Date().toLocaleString()}.</p>
        ${renderedSections}
      </body>
    </html>
  `);
  popup.document.close();
  popup.focus();
  popup.print();
}
