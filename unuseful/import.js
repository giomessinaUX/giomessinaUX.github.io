import React from 'react';
import { useTranslation } from 'react-i18next';

const ContentParagraph = ({ id, content, pdfUrl }) => {
  const { t, i18n } = useTranslation();

  return (
    <div id={id}>
      <p>{t(content)}</p>
      <a href={pdfUrl} download>{t('downloadPdf')}</a>
      <button onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'it' : 'en')}>
        {t('switchLanguage')}
      </button>
    </div>
  );
};

export default ContentParagraph;