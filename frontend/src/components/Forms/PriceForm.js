import React, { useEffect, useState } from "react";
import { Container, Row, Col, Button, Input, FormText } from "reactstrap";

function PriceForm() {
  const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
  const [form, setForm] = useState({
    manufacturer: "",
    model: "",
    year: "",
    odometer: "",
    title_status: "",
    transmission: "",
    paint_color: "",
    state: "",
  });
  const [options, setOptions] = useState({
    manufacturers: [],
    models: [],
    colors: [],
    transmissions: [],
    states: [],
  });
  const [status, setStatus] = useState({ error: "", loading: false });

  const [prediction, setPrediction] = useState(null);

  const fetchJson = async (path) => {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) {
      throw new Error(`Request failed with ${res.status}`);
    }
    return res.json();
  };

  useEffect(() => {
    const loadManufacturers = async () => {
      try {
        const data = await fetchJson("/options/manufacturers");
        setOptions((prev) => ({
          ...prev,
          manufacturers: data.manufacturers || [],
        }));
      } catch (error) {
        console.error("Failed to load manufacturers", error);
        setStatus({ error: "Unable to load vehicle metadata.", loading: false });
      }
    };
    loadManufacturers();
  }, []);

  useEffect(() => {
    const loadModelDetails = async () => {
      if (!form.manufacturer || !form.model) {
        setOptions((prev) => ({
          ...prev,
          colors: [],
          transmissions: [],
          states: [],
        }));
        return;
      }
      try {
        const params = new URLSearchParams({
          manufacturer: form.manufacturer,
          model: form.model,
        });
        const data = await fetchJson(`/options/model-details?${params.toString()}`);
        setOptions((prev) => ({
          ...prev,
          colors: data.colors || [],
          transmissions: data.transmissions || [],
          states: data.states || [],
        }));
      } catch (error) {
        console.error("Failed to load model metadata", error);
        setStatus({ error: "Unable to load model details.", loading: false });
      }
    };
    loadModelDetails();
  }, [form.manufacturer, form.model]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setStatus({ error: "", loading: false });
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleManufacturerChange = async (e) => {
    const value = e.target.value;
    setForm((prev) => ({
      ...prev,
      manufacturer: value,
      model: "",
      paint_color: "",
      transmission: "",
      state: "",
    }));
    setStatus({ error: "", loading: false });
    if (!value) {
      setOptions((prev) => ({
        ...prev,
        models: [],
        colors: [],
        transmissions: [],
        states: [],
      }));
      return;
    }
    try {
      const params = new URLSearchParams({ manufacturer: value });
      const data = await fetchJson(`/options/models?${params.toString()}`);
      setOptions((prev) => ({
        ...prev,
        models: data.models || [],
        colors: [],
        transmissions: [],
        states: [],
      }));
    } catch (error) {
      console.error("Failed to load models", error);
      setStatus({ error: "Unable to load models for that manufacturer.", loading: false });
    }
  };

  const handlePredict = async () => {
    const requiredFields = [
      "manufacturer",
      "model",
      "year",
      "odometer",
      "title_status",
      "transmission",
      "paint_color",
      "state",
    ];
    const missing = requiredFields.filter((field) => !form[field]);
    if (missing.length) {
      setStatus({
        error: "Please complete all fields before requesting a price.",
        loading: false,
      });
      return;
    }
    setStatus({ error: "", loading: true });
    try {
      const payload = {
        ...form,
        year: Number(form.year),
        odometer: Number(form.odometer),
      };
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error?.detail || "Prediction failed");
      }
      const data = await res.json();
      setPrediction(data.predicted_price);
    } catch (error) {
      console.error("Prediction failed", error);
      setPrediction(null);
      setStatus({ error: "The model could not compute a price.", loading: false });
    } finally {
      setStatus((prev) => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="section">
      <Container>
        <h2 className="title text-center">Vehicle Price Estimator</h2>

        <Row>
          <Col md="6">
            <label>Manufacturer</label>
            <Input
              type="select"
              name="manufacturer"
              value={form.manufacturer}
              onChange={handleManufacturerChange}
            >
              <option value="">Select</option>
              {options.manufacturers.map((manufacturer) => (
                <option key={manufacturer} value={manufacturer}>
                  {manufacturer}
                </option>
              ))}
            </Input>
          </Col>
          <Col md="6">
            <label>Model</label>
            <Input
              type="select"
              name="model"
              value={form.model}
              onChange={handleChange}
              disabled={!options.models.length}
            >
              <option value="">{options.models.length ? "Select" : "Select a manufacturer first"}</option>
              {options.models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </Input>
          </Col>
          <Col md="6">
            <label>Year</label>
            <Input
              name="year"
              type="number"
              value={form.year}
              onChange={handleChange}
              placeholder="e.g. 2019"
            />
          </Col>
          <Col md="6">
            <label>Mileage</label>
            <Input
              name="odometer"
              type="number"
              value={form.odometer}
              onChange={handleChange}
              placeholder="e.g. 45000"
            />
          </Col>
          <Col md="6">
            <label>Condition</label>
            <Input type="select" name="title_status" value={form.title_status} onChange={handleChange}>
              <option value="">Select</option>
              <option value="clean">Clean</option>
              <option value="rebuilt">Rebuilt</option>
              <option value="salvage">Salvage</option>
            </Input>
          </Col>

          <Col md="6">
            <label>Transmission</label>
            {options.transmissions.length ? (
              <Input
                type="select"
                name="transmission"
                value={form.transmission}
                onChange={handleChange}
              >
                <option value="">Select</option>
                {options.transmissions.map((transmission) => (
                  <option key={transmission} value={transmission}>
                    {transmission}
                  </option>
                ))}
              </Input>
            ) : (
              <Input
                name="transmission"
                value={form.transmission}
                onChange={handleChange}
                placeholder={form.model ? "Enter transmission" : "Select a model first"}
                disabled={!form.model}
              />
            )}
          </Col>

          <Col md="6">
            <label>Paint Color</label>
            {options.colors.length ? (
              <Input
                type="select"
                name="paint_color"
                value={form.paint_color}
                onChange={handleChange}
              >
                <option value="">Select</option>
                {options.colors.map((color) => (
                  <option key={color} value={color}>
                    {color}
                  </option>
                ))}
              </Input>
            ) : (
              <Input
                name="paint_color"
                value={form.paint_color}
                onChange={handleChange}
                placeholder={form.model ? "Enter color" : "Select a model first"}
                disabled={!form.model}
              />
            )}
          </Col>

          <Col md="6">
            <label>State</label>
            {options.states.length ? (
              <Input
                type="select"
                name="state"
                value={form.state}
                onChange={handleChange}
              >
                <option value="">Select</option>
                {options.states.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </Input>
            ) : (
              <Input
                name="state"
                value={form.state}
                onChange={handleChange}
                placeholder={form.model ? "Enter state (e.g. CA)" : "Select a model first"}
                disabled={!form.model}
              />
            )}
          </Col>
        </Row>
        <div className="text-center mt-4">
          <Button color="primary" onClick={handlePredict}>
            {status.loading ? "Predicting..." : "Predict Price"}
          </Button>
          {status.error && <FormText color="danger" className="mt-2">{status.error}</FormText>}
        </div>

        {prediction && (
          <div className="text-center mt-4">
            <h3>Estimated Price:</h3>
            <h2 className="title text-success">${prediction.toLocaleString()}</h2>
          </div>
        )}
      </Container>
    </div>
  );
}

export default PriceForm;
