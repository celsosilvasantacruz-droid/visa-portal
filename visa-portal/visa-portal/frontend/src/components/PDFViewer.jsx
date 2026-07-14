import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Spinner, Alert, Button, Card } from 'react-bootstrap';
import { Document, Page, pdfjs } from 'react-pdf';
import toast from 'react-hot-toast';
import api from '../services/api';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const POLL_INTERVAL_MS = 4000;

const PDFViewer = () => {
  const { applicationId } = useParams();
  const [application, setApplication] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);

  const fetchApplication = useCallback(async () => {
    try {
      const res = await api.get(`/applications/${applicationId}/`);
      setApplication(res.data);
      setError(null);
    } catch (err) {
      setError('Não foi possível carregar a candidatura.');
    } finally {
      setLoading(false);
    }
  }, [applicationId]);

  useEffect(() => {
    fetchApplication();
  }, [fetchApplication]);

  useEffect(() => {
    if (application && !application.pdf_generated) {
      const interval = setInterval(fetchApplication, POLL_INTERVAL_MS);
      return () => clearInterval(interval);
    }
  }, [application, fetchApplication]);

  const handleSendToEmbassy = async () => {
    setSending(true);
    try {
      await api.post(`/applications/${applicationId}/send_to_embassy/`);
      toast.success('Candidatura enviada para a embaixada!');
      fetchApplication();
    } catch (err) {
      const message = err.response?.data?.error || 'Erro ao enviar para a embaixada.';
      toast.error(message);
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" />
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">{error}</Alert>
        <Link to="/dashboard">Voltar ao painel</Link>
      </Container>
    );
  }

  return (
    <Container className="py-5 text-center" style={{ maxWidth: 700 }}>
      <h3 className="mb-4">Candidatura #{application.id}</h3>

      {!application.pdf_generated ? (
        <Card className="p-4 shadow-sm">
          <Spinner animation="border" className="mx-auto mb-3" />
          <p>O PDF ainda está a ser gerado. Esta página atualiza-se automaticamente.</p>
        </Card>
      ) : (
        <Card className="p-3 shadow-sm">
          <Document
            file={application.pdf_generated}
            onLoadSuccess={({ numPages }) => setNumPages(numPages)}
            onLoadError={() => setError('Não foi possível carregar o PDF.')}
          >
            {Array.from(new Array(numPages || 0), (_, index) => (
              <Page key={`page_${index + 1}`} pageNumber={index + 1} width={600} />
            ))}
          </Document>

          <div className="d-flex gap-2 mt-3">
            <a
              href={application.pdf_generated}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline-primary w-100"
            >
              Descarregar PDF
            </a>
            <Button
              variant="success"
              className="w-100"
              onClick={handleSendToEmbassy}
              disabled={sending || application.status === 'completed'}
            >
              {sending ? <Spinner animation="border" size="sm" /> :
                application.status === 'completed' ? 'Já enviado' : 'Enviar para a Embaixada'}
            </Button>
          </div>
        </Card>
      )}

      <Link to="/dashboard" className="d-block mt-4">Voltar ao painel</Link>
    </Container>
  );
};

export default PDFViewer;
