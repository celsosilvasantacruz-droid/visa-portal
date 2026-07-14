import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Button, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [visas, setVisas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/visas/').then(res => {
      setVisas(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <Container className="text-center mt-5"><Spinner animation="border" /></Container>;

  return (
    <Container className="py-5">
      <h2 className="mb-4">Tipos de Vistos Disponíveis</h2>
      <Row>
        {visas.map(visa => (
          <Col md={4} key={visa.id} className="mb-4">
            <Card className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>{visa.country_name} - {visa.name}</Card.Title>
                <Card.Text>{visa.description}</Card.Text>
                <Card.Text className="fw-bold text-primary">Preço: {visa.price_service}€</Card.Text>
                <Link to={`/apply/${visa.id}`} className="btn btn-primary w-100">Iniciar Candidatura</Link>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default Dashboard;
