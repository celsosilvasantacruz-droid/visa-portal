import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Form, Button, Spinner, Card, Alert } from 'react-bootstrap';
import { useForm, Controller } from 'react-hook-form';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import api from '../services/api';

const FileDropzone = ({ field, onFileSelect }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onFileSelect(field.id, acceptedFiles[0]);
    }
  }, [field, onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
    accept: { 'image/*': [], 'application/pdf': [] },
  });

  return (
    <div
      {...getRootProps()}
      className={`border rounded p-3 text-center ${isDragActive ? 'bg-light border-primary' : 'border-secondary'}`}
      style={{ cursor: 'pointer' }}
    >
      <input {...getInputProps()} />
      {acceptedFiles.length > 0 ? (
        <span>{acceptedFiles[0].name}</span>
      ) : (
        <span>Arrasta um ficheiro ou clica aqui (imagem ou PDF, máx. 5MB)</span>
      )}
    </div>
  );
};

const VisaApplication = () => {
  const { visaId } = useParams();
  const navigate = useNavigate();
  const { register, control, handleSubmit, formState: { errors } } = useForm();

  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [applicationId, setApplicationId] = useState(null);
  const [files, setFiles] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    const init = async () => {
      try {
        const fieldsRes = await api.get(`/visas/${visaId}/fields/`);
        setFields(fieldsRes.data);

        const appRes = await api.post('/applications/', { visa_type: visaId });
        setApplicationId(appRes.data.id);
      } catch (err) {
        setError('Não foi possível carregar o formulário de candidatura.');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [visaId]);

  const handleFileSelect = (fieldId, file) => {
    setFiles(prev => ({ ...prev, [fieldId]: file }));
  };

  const onSubmit = async (formValues) => {
    if (!applicationId) return;
    setSubmitting(true);

    try {
      const textFields = fields
        .filter(f => f.field_type !== 'file')
        .map(f => ({ field_id: f.id, value_text: formValues[`field_${f.id}`] || '' }));

      const formData = new FormData();
      formData.append('fields', JSON.stringify(textFields));

      fields.filter(f => f.field_type === 'file').forEach(f => {
        const file = files[f.id];
        if (file) formData.append(`field_${f.id}`, file);
      });

      await api.post(`/applications/${applicationId}/submit_data/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success('Candidatura submetida com sucesso!');
      navigate(`/pdf/${applicationId}`);
    } catch (err) {
      const message = err.response?.data?.error || 'Erro ao submeter a candidatura.';
      toast.error(message);
    } finally {
      setSubmitting(false);
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
      </Container>
    );
  }

  return (
    <Container className="py-5" style={{ maxWidth: 700 }}>
      <Card className="shadow-sm p-4">
        <h3 className="mb-4">Formulário de Candidatura</h3>
        <Form onSubmit={handleSubmit(onSubmit)}>
          {fields.map(field => (
            <Form.Group className="mb-3" key={field.id}>
              <Form.Label>
                {field.label} {field.is_required && <span className="text-danger">*</span>}
              </Form.Label>

              {field.field_type === 'file' ? (
                <Controller
                  name={`field_${field.id}`}
                  control={control}
                  rules={{ required: field.is_required }}
                  render={() => (
                    <FileDropzone field={field} onFileSelect={handleFileSelect} />
                  )}
                />
              ) : field.field_type === 'textarea' ? (
                <Form.Control
                  as="textarea"
                  rows={3}
                  placeholder={field.placeholder}
                  {...register(`field_${field.id}`, { required: field.is_required })}
                />
              ) : (
                <Form.Control
                  type={field.field_type === 'number' ? 'number' : field.field_type === 'date' ? 'date' : field.field_type}
                  placeholder={field.placeholder}
                  {...register(`field_${field.id}`, {
                    required: field.is_required,
                    pattern: field.validation_regex ? new RegExp(field.validation_regex) : undefined,
                  })}
                />
              )}

              {field.help_text && <Form.Text muted>{field.help_text}</Form.Text>}
              {errors[`field_${field.id}`] && (
                <div className="text-danger small mt-1">Este campo é obrigatório ou inválido.</div>
              )}
            </Form.Group>
          ))}

          <Button type="submit" variant="primary" className="w-100" disabled={submitting}>
            {submitting ? <Spinner animation="border" size="sm" /> : 'Submeter Candidatura'}
          </Button>
        </Form>
      </Card>
    </Container>
  );
};

export default VisaApplication;
