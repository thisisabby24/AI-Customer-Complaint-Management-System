import { useEffect, useState } from "react";
import axios from "axios";
import { useDispatch, useSelector } from "react-redux";

import {
  setComplaintData,
  setRiskData,
  setLoading,
  setError,
  clearError,
  setStatus,
  setSelectedFile,
  resetComplaint,
} from "./store/complaintsSlice";

function App() {
  const dispatch = useDispatch();

  const reduxState = useSelector(
    (state) => state.complaints || {}
  );

  const complaintData =
    reduxState.complaintData || {};

  const riskData =
    reduxState.riskData || {};

  const loading =
    reduxState.loading || false;

  const error =
    reduxState.error || null;

  const status =
    reduxState.status ||
    "PENDING_TRIAGE";

  const selectedFile =
    reduxState.selectedFile || null;

  // --------------------------------------------------
  // COMPLAINT TEXT
  // --------------------------------------------------

  const [complaintText, setComplaintText] =
    useState("");

  // --------------------------------------------------
  // AI ASSISTANT
  // --------------------------------------------------

  const [assistantCommand, setAssistantCommand] =
    useState("");

  const [assistantMessages, setAssistantMessages] =
    useState([
      {
        role: "assistant",
        text:
          "Hello! I can help you review or update complaint information. Try saying: Change the batch number to AMX240603.",
      },
    ]);

  const [assistantLoading, setAssistantLoading] =
    useState(false);

  // --------------------------------------------------
  // DASHBOARD
  // --------------------------------------------------

  const [complaints, setComplaints] =
    useState([]);

  const [dashboardLoading, setDashboardLoading] =
    useState(false);

  // --------------------------------------------------
  // LOAD COMPLAINTS FROM DATABASE
  // --------------------------------------------------

  const fetchComplaints = async () => {
    setDashboardLoading(true);

    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/complaints/"
      );

      const data =
        response.data || [];

      if (Array.isArray(data)) {
        setComplaints(data);
      } else if (
        Array.isArray(data.complaints)
      ) {
        setComplaints(data.complaints);
      } else {
        setComplaints([]);
      }

    } catch (err) {
      console.error(
        "Dashboard loading error:",
        err
      );
    } finally {
      setDashboardLoading(false);
    }
  };

  // Load dashboard when application starts
  useEffect(() => {
    fetchComplaints();
  }, []);

  // --------------------------------------------------
  // DYNAMIC DASHBOARD COUNTS
  // --------------------------------------------------

  const totalComplaints =
    complaints.length;

  const majorComplaints =
    complaints.filter(
      (complaint) =>
        String(
          complaint.severity || ""
        ).toLowerCase() === "major"
    ).length;

  const criticalComplaints =
    complaints.filter(
      (complaint) =>
        String(
          complaint.severity || ""
        ).toLowerCase() === "critical"
    ).length;

  const highPriorityComplaints =
    complaints.filter(
      (complaint) =>
        String(
          complaint.priority || ""
        ).toLowerCase() === "high"
    ).length;

  // --------------------------------------------------
  // FORM INPUT
  // --------------------------------------------------

  const handleInputChange = (
    field,
    value
  ) => {
    dispatch(
      setComplaintData({
        [field]: value,
      })
    );
  };

  // --------------------------------------------------
  // COMPLAINT TEXT
  // --------------------------------------------------

  const handleTextChange = (
    event
  ) => {
    setComplaintText(
      event.target.value
    );
  };

  // --------------------------------------------------
  // PDF FILE
  // --------------------------------------------------

  const handleFileChange = (
    event
  ) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    if (
      file.type !==
        "application/pdf" &&
      !file.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {
      dispatch(
        setError(
          "Please select a PDF file."
        )
      );

      return;
    }

    dispatch(
      setSelectedFile(file)
    );

    dispatch(clearError());
  };

  // --------------------------------------------------
  // AI EXTRACTION + RISK ASSESSMENT
  // TEXT OR PDF
  // --------------------------------------------------

  const extractAndAssess =
    async () => {

      if (
        !selectedFile &&
        !complaintText.trim()
      ) {
        dispatch(
          setError(
            "Please paste complaint text or select a PDF file."
          )
        );

        return;
      }

      dispatch(setLoading(true));
      dispatch(clearError());
      dispatch(
        setStatus("PROCESSING")
      );

      try {
        let response;

        // -------------------------------------------
        // PDF WORKFLOW
        // -------------------------------------------

        if (selectedFile) {
          const formData =
            new FormData();

          formData.append(
            "file",
            selectedFile
          );

          response =
            await axios.post(
              "http://127.0.0.1:8000/api/complaints/process-pdf",
              formData
            );
        }

        // -------------------------------------------
        // TEXT WORKFLOW
        // -------------------------------------------

        else {
          response =
            await axios.post(
              "http://127.0.0.1:8000/api/complaints/process",
              {
                complaint_text:
                  complaintText,
              }
            );
        }

        console.log(
          "AI PROCESS RESPONSE:"
        );

        console.log(
          response.data
        );

        const data =
          response.data || {};

        const extractedData =
          data.extracted_data ||
          data.extracted_complaint ||
          data.complaint_data ||
          data.complaint ||
          {};

        const extractedRisk =
          data.risk_data ||
          data.risk_assessment ||
          data.risk ||
          {};

        if (
          Object.keys(
            extractedData
          ).length > 0
        ) {
          dispatch(
            setComplaintData(
              extractedData
            )
          );
        }

        if (
          Object.keys(
            extractedRisk
          ).length > 0
        ) {
          dispatch(
            setRiskData(
              extractedRisk
            )
          );
        }

        dispatch(
          setStatus(
            "UNDER_INVESTIGATION"
          )
        );

        setAssistantMessages(
          (previous) => [
            ...previous,
            {
              role: "assistant",
              text:
                "Complaint information has been extracted and assessed successfully. You can review the fields on the left or ask me to update something.",
            },
          ]
        );

      } catch (err) {

        console.error(
          "AI processing error:",
          err
        );

        let message =
          "Unable to process the complaint.";

        if (
          err.response?.data?.detail
        ) {
          if (
            typeof err.response.data
              .detail === "string"
          ) {
            message =
              err.response.data.detail;
          } else {
            message =
              JSON.stringify(
                err.response.data.detail
              );
          }
        }

        dispatch(
          setError(message)
        );

        dispatch(
          setStatus(
            "PENDING_TRIAGE"
          )
        );

      } finally {
        dispatch(
          setLoading(false)
        );
      }
    };

  // --------------------------------------------------
  // SAVE COMPLAINT
  // --------------------------------------------------

  const saveComplaint =
    async () => {

      dispatch(clearError());
      dispatch(setLoading(true));

      try {

        const response =
          await axios.post(
            "http://127.0.0.1:8000/api/complaints/",
            complaintData
          );

        console.log(
          "COMPLAINT SAVED:"
        );

        console.log(
          response.data
        );

        dispatch(
          setStatus(
            "UNDER_INVESTIGATION"
          )
        );

        alert(
          `Complaint saved successfully.\nComplaint ID: ${
            response.data.complaint_id ||
            response.data.id ||
            "Created"
          }`
        );

        // Refresh dashboard immediately
        await fetchComplaints();

      } catch (err) {

        console.error(
          "Save complaint error:",
          err
        );

        let message =
          "Unable to save complaint.";

        if (
          err.response?.data?.detail
        ) {
          if (
            typeof err.response.data
              .detail === "string"
          ) {
            message =
              err.response.data.detail;
          } else {
            message =
              JSON.stringify(
                err.response.data.detail
              );
          }
        }

        dispatch(
          setError(message)
        );

      } finally {

        dispatch(
          setLoading(false)
        );
      }
    };

  // --------------------------------------------------
  // AI ASSISTANT
  // --------------------------------------------------

  const sendAssistantCommand =
    async () => {

      const command =
        assistantCommand.trim();

      if (!command) {
        return;
      }

      setAssistantMessages(
        (previous) => [
          ...previous,
          {
            role: "user",
            text: command,
          },
        ]
      );

      setAssistantCommand("");
      setAssistantLoading(true);
      dispatch(clearError());

      try {

        const response =
          await axios.post(
            "http://127.0.0.1:8000/api/assistant/command",
            {
              command,
              current_complaint:
                complaintData,
            }
          );

        console.log(
          "ASSISTANT RESPONSE:"
        );

        console.log(
          response.data
        );

        const result =
          response.data?.result ||
          {};

        // -------------------------------------------
        // UPDATE FORM FIELD
        // -------------------------------------------

        if (
          result.action ===
            "update" &&
          result.field
        ) {

          dispatch(
            setComplaintData({
              [result.field]:
                result.value,
            })
          );

          setAssistantMessages(
            (previous) => [
              ...previous,
              {
                role: "assistant",
                text:
                  result.message ||
                  "Complaint field updated successfully.",
              },
            ]
          );

          return;
        }

        // -------------------------------------------
        // ANSWER USER QUESTION
        // -------------------------------------------

        setAssistantMessages(
          (previous) => [
            ...previous,
            {
              role: "assistant",
              text:
                result.message ||
                "Command processed successfully.",
            },
          ]
        );

      } catch (err) {

        console.error(
          "Assistant error:",
          err
        );

        let message =
          "Unable to process assistant command.";

        if (
          err.response?.data?.detail
        ) {
          if (
            typeof err.response.data
              .detail === "string"
          ) {
            message =
              err.response.data.detail;
          } else {
            message =
              JSON.stringify(
                err.response.data.detail
              );
          }
        }

        setAssistantMessages(
          (previous) => [
            ...previous,
            {
              role: "assistant",
              text: message,
            },
          ]
        );

      } finally {

        setAssistantLoading(
          false
        );
      }
    };

  // --------------------------------------------------
  // ASSISTANT ENTER KEY
  // --------------------------------------------------

  const handleAssistantKeyDown =
    (event) => {

      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {
        event.preventDefault();

        sendAssistantCommand();
      }
    };

  // --------------------------------------------------
  // RESET
  // --------------------------------------------------

  const handleReset = () => {

    setComplaintText("");
    setAssistantCommand("");

    setAssistantMessages([
      {
        role: "assistant",
        text:
          "Hello! I can help you review or update complaint information. Try saying: Change the batch number to AMX240603.",
      },
    ]);

    dispatch(
      resetComplaint()
    );
  };

  // --------------------------------------------------
  // SAFE RISK DATA
  // --------------------------------------------------

  const riskCategory =
    riskData?.risk_category ??
    riskData?.category ??
    riskData?.riskCategory ??
    complaintData?.risk_category ??
    null;

  const riskScore =
    riskData?.risk_score ??
    riskData?.score ??
    riskData?.riskScore ??
    complaintData?.risk_score ??
    null;

  const riskAssessment =
    riskData?.risk_assessment ??
    riskData?.assessment ??
    riskData?.riskAssessment ??
    complaintData?.risk_assessment ??
    null;

  const suggestedAction =
    riskData?.suggested_action ??
    riskData?.action ??
    riskData?.suggestedAction ??
    complaintData?.suggested_action ??
    null;

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="app">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="app-header">

        <div>

          <h1>
            AI Complaint Management System
          </h1>

          <p>
            Pharmaceutical Customer Complaint Management
          </p>

        </div>

        <div className="status-badge">
          {status}
        </div>

      </header>

      <main className="page-container">

        {/* ==================================================
            DASHBOARD
        ================================================== */}

        <section className="dashboard-section">

          <div className="section-heading">

            <h2>
              Complaint Dashboard
            </h2>

            <p>
              Overview of complaints recorded in the QMS database
            </p>

          </div>

          <div className="dashboard-actions">

            <button
              type="button"
              className="secondary-button"
              onClick={
                fetchComplaints
              }
              disabled={
                dashboardLoading
              }
            >
              {dashboardLoading
                ? "Refreshing..."
                : "Refresh"}
            </button>

          </div>

          <div className="dashboard-cards">

            <div className="dashboard-card">

              <span>
                Total Complaints
              </span>

              <strong>
                {dashboardLoading
                  ? "..."
                  : totalComplaints}
              </strong>

            </div>

            <div className="dashboard-card">

              <span>
                Major Complaints
              </span>

              <strong>
                {dashboardLoading
                  ? "..."
                  : majorComplaints}
              </strong>

            </div>

            <div className="dashboard-card">

              <span>
                Critical Complaints
              </span>

              <strong>
                {dashboardLoading
                  ? "..."
                  : criticalComplaints}
              </strong>

            </div>

            <div className="dashboard-card">

              <span>
                High Priority
              </span>

              <strong>
                {dashboardLoading
                  ? "..."
                  : highPriorityComplaints}
              </strong>

            </div>

          </div>

        </section>

        {/* ==================================================
            MAIN GRID
        ================================================== */}

        <div className="main-grid">

          {/* ==================================================
              LEFT SIDE - COMPLAINT FORM
          ================================================== */}

          <section className="complaint-card">

            <div className="card-heading">

              <h2>
                Log Customer Complaint
              </h2>

              <p>
                Review and manage complaint information
              </p>

            </div>

            {/* ==================================================
                SECTION 1
            ================================================== */}

            <div className="form-section">

              <h3>
                1. Origin &amp; Customer Details
              </h3>

              <div className="form-grid">

                <div className="form-group">

                  <label>
                    Complaint Source
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.complaint_source ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "complaint_source",
                        event.target.value
                      )
                    }
                    placeholder="Enter complaint source"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Customer Name
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.customer_name ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "customer_name",
                        event.target.value
                      )
                    }
                    placeholder="Enter customer name"
                  />

                </div>

              </div>

            </div>

            {/* ==================================================
                SECTION 2
            ================================================== */}

            <div className="form-section">

              <h3>
                2. Product &amp; Batch Identification
              </h3>

              <div className="form-grid">

                <div className="form-group">

                  <label>
                    Product Name (API/FDF)
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.product_name ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "product_name",
                        event.target.value
                      )
                    }
                    placeholder="Enter product name"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Product Strength / Grade
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.product_strength ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "product_strength",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 500 mg"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Batch / Lot Number
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.batch_number ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "batch_number",
                        event.target.value
                      )
                    }
                    placeholder="Enter batch number"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Affected Quantity
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.affected_quantity ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "affected_quantity",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 12 capsules"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Manufacturing Date
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.manufacturing_date ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "manufacturing_date",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 1 March 2026"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Expiry Date
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.expiry_date ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "expiry_date",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 28 February 2028"
                  />

                </div>

              </div>

            </div>

            {/* ==================================================
                SECTION 3
            ================================================== */}

            <div className="form-section">

              <h3>
                3. Complaint Details
              </h3>

              <div className="form-grid">

                <div className="form-group">

                  <label>
                    Complaint Type
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.complaint_type ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "complaint_type",
                        event.target.value
                      )
                    }
                    placeholder="e.g. Product Quality"
                  />

                </div>

                <div className="form-group">

                  <label>
                    Complaint Date
                  </label>

                  <input
                    type="text"
                    value={
                      complaintData.complaint_date ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "complaint_date",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 11 September 2026"
                  />

                </div>

              </div>

              <div className="form-group full-width">

                <label>
                  Detailed Complaint Description
                </label>

                <textarea
                  value={
                    complaintData.complaint_description ||
                    ""
                  }
                  onChange={(event) =>
                    handleInputChange(
                      "complaint_description",
                      event.target.value
                    )
                  }
                  placeholder="Enter detailed complaint description"
                />

              </div>

            </div>

            {/* ==================================================
                SECTION 4
            ================================================== */}

            <div className="form-section">

              <h3>
                4. Initial Assessment / Priority
              </h3>

              <div className="form-grid">

                <div className="form-group">

                  <label>
                    Initial Severity
                  </label>

                  <select
                    value={
                      complaintData.severity ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "severity",
                        event.target.value
                      )
                    }
                  >

                    <option value="">
                      Select severity
                    </option>

                    <option value="Minor">
                      Minor
                    </option>

                    <option value="Medium">
                      Medium
                    </option>

                    <option value="Major">
                      Major
                    </option>

                    <option value="Critical">
                      Critical
                    </option>

                  </select>

                </div>

                <div className="form-group">

                  <label>
                    Priority
                  </label>

                  <select
                    value={
                      complaintData.priority ||
                      ""
                    }
                    onChange={(event) =>
                      handleInputChange(
                        "priority",
                        event.target.value
                      )
                    }
                  >

                    <option value="">
                      Select priority
                    </option>

                    <option value="Low">
                      Low
                    </option>

                    <option value="Medium">
                      Medium
                    </option>

                    <option value="High">
                      High
                    </option>

                    <option value="Critical">
                      Critical
                    </option>

                  </select>

                </div>

              </div>

              {/* ==================================================
                  AI RISK ASSESSMENT
              ================================================== */}

              {(riskScore !== null ||
                riskCategory ||
                riskAssessment ||
                suggestedAction) && (

                <div className="risk-card">

                  <h3>
                    AI Risk Assessment
                  </h3>

                  {riskCategory && (
                    <p>
                      <strong>
                        Risk Category:
                      </strong>{" "}
                      {riskCategory}
                    </p>
                  )}

                  {riskScore !== null && (
                    <p>
                      <strong>
                        Risk Score:
                      </strong>{" "}
                      {riskScore} / 10
                    </p>
                  )}

                  {riskAssessment && (
                    <p>
                      <strong>
                        Risk Assessment:
                      </strong>{" "}
                      {riskAssessment}
                    </p>
                  )}

                  {suggestedAction && (
                    <p>
                      <strong>
                        Suggested Action:
                      </strong>{" "}
                      {suggestedAction}
                    </p>
                  )}

                </div>

              )}

            </div>

            {/* ==================================================
                FORM BUTTONS
            ================================================== */}

            <div className="form-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={handleReset}
              >
                Reset Form
              </button>

              <button
                type="button"
                className="primary-button"
                onClick={saveComplaint}
                disabled={loading}
              >
                {loading
                  ? "Saving..."
                  : "Save Complaint"}
              </button>

            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

          </section>

          {/* ==================================================
              RIGHT SIDE - AI ASSISTANT
          ================================================== */}

          <section className="ai-card">

            <div className="card-heading">

              <h2>
                AI Complaint Intake Assistant
              </h2>

              <p>
                Use AI to extract, assess and update complaint information
              </p>

            </div>

            {/* ==================================================
                PDF UPLOAD
            ================================================== */}

            <div className="upload-box">

              <div className="upload-icon">
                ↑
              </div>

              <h3>
                Upload Complaint
              </h3>

              <p>
                Drag &amp; drop a complaint PDF here or browse files
              </p>

              <label className="browse-button">

                Browse Files

                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={
                    handleFileChange
                  }
                  hidden
                />

              </label>

              <span className="file-support">
                PDF files supported
              </span>

              {selectedFile && (
                <div className="selected-file">

                  Selected:{" "}

                  <strong>
                    {selectedFile.name}
                  </strong>

                </div>
              )}

            </div>

            {/* ==================================================
                TEXT INPUT
            ================================================== */}

            <div className="ai-input-section">

              <label>
                Paste Complaint Text / Email
              </label>

              <textarea
                value={
                  complaintText
                }
                onChange={
                  handleTextChange
                }
                placeholder="Paste a customer complaint or email here..."
              />

              <div className="example-text">

                <strong>
                  Example:
                </strong>

                <p>
                  Apollo Pharmacy reported a complaint on
                  11 September 2026 regarding Amoxicillin
                  Capsules 500 mg, batch AMX240602. The
                  customer received a sealed bottle containing
                  12 discolored capsules. The manufacturing date
                  was 1 March 2026 and the expiry date is
                  28 February 2028. The customer requested an
                  investigation into the product quality.
                </p>

              </div>

              <button
                type="button"
                className="ai-button"
                onClick={
                  extractAndAssess
                }
                disabled={loading}
              >
                {loading
                  ? "Processing with AI..."
                  : "Extract & Assess with AI"}
              </button>

            </div>

            {/* ==================================================
                AI ASSISTANT CHAT
            ================================================== */}

            <div
              className="assistant-chat"
              style={{
                marginTop: "24px",
                padding: "18px",
                border:
                  "1px solid #e5e7eb",
                borderRadius: "14px",
                background:
                  "#fafafa",
              }}
            >

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "14px",
                }}
              >

                <div className="assistant-icon">
                  AI
                </div>

                <div>

                  <h3
                    style={{
                      margin: 0,
                    }}
                  >
                    AI Complaint Assistant
                  </h3>

                  <p
                    style={{
                      margin:
                        "4px 0 0",
                      fontSize:
                        "13px",
                      opacity: 0.7,
                    }}
                  >
                    Ask questions or update complaint fields using natural language.
                  </p>

                </div>

              </div>

              {/* CHAT MESSAGES */}

              <div
                style={{
                  maxHeight:
                    "300px",
                  overflowY:
                    "auto",
                  display:
                    "flex",
                  flexDirection:
                    "column",
                  gap: "10px",
                  marginBottom:
                    "14px",
                }}
              >

                {assistantMessages.map(
                  (
                    message,
                    index
                  ) => (

                    <div
                      key={index}
                      style={{
                        display:
                          "flex",
                        justifyContent:
                          message.role ===
                          "user"
                            ? "flex-end"
                            : "flex-start",
                      }}
                    >

                      <div
                        style={{
                          maxWidth:
                            "85%",
                          padding:
                            "10px 13px",
                          borderRadius:
                            "12px",
                          background:
                            message.role ===
                            "user"
                              ? "#111827"
                              : "#ffffff",
                          color:
                            message.role ===
                            "user"
                              ? "#ffffff"
                              : "#111827",
                          border:
                            message.role ===
                            "user"
                              ? "none"
                              : "1px solid #e5e7eb",
                          fontSize:
                            "14px",
                          lineHeight:
                            1.5,
                        }}
                      >
                        {message.text}
                      </div>

                    </div>

                  )
                )}

                {assistantLoading && (
                  <div
                    style={{
                      fontSize:
                        "13px",
                      opacity: 0.65,
                    }}
                  >
                    AI is processing...
                  </div>
                )}

              </div>

              {/* CHAT INPUT */}

              <div
                style={{
                  display:
                    "flex",
                  gap: "8px",
                }}
              >

                <input
                  type="text"
                  value={
                    assistantCommand
                  }
                  onChange={(
                    event
                  ) =>
                    setAssistantCommand(
                      event.target
                        .value
                    )
                  }
                  onKeyDown={
                    handleAssistantKeyDown
                  }
                  placeholder="e.g. Change batch number to AMX240603"
                  disabled={
                    assistantLoading
                  }
                  style={{
                    flex: 1,
                    padding:
                      "11px 12px",
                    border:
                      "1px solid #d1d5db",
                    borderRadius:
                      "9px",
                    outline:
                      "none",
                  }}
                />

                <button
                  type="button"
                  className="primary-button"
                  onClick={
                    sendAssistantCommand
                  }
                  disabled={
                    assistantLoading ||
                    !assistantCommand.trim()
                  }
                >
                  Send
                </button>

              </div>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}

export default App;