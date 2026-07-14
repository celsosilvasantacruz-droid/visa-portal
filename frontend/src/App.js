import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './components/Dashboard';
import VisaApplication from './components/VisaApplication';
import PDFViewer from './components/PDFViewer';

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/apply/:visaId" element={<VisaApplication />} />
        <Route path="/pdf/:applicationId" element={<PDFViewer />} />
      </Routes>
    </Router>
  );
}

export default App;
