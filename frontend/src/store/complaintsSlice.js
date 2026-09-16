import { createSlice } from "@reduxjs/toolkit";

const initialComplaintData = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength: "",
  batch_number: "",
  affected_quantity: "",
  manufacturing_date: "",
  expiry_date: "",
  complaint_date: "",
  complaint_type: "",
  complaint_description: "",
  severity: "",
  priority: "",
  risk_category: "",
  risk_score: null,
  risk_assessment: "",
  suggested_action: "",
};

const initialState = {
  complaintData: initialComplaintData,
  riskData: {},
  loading: false,
  error: null,
  status: "PENDING_TRIAGE",
  selectedFile: null,
};

const complaintsSlice = createSlice({
  name: "complaints",

  initialState,

  reducers: {
    // --------------------------------------------------
    // COMPLAINT DATA
    // --------------------------------------------------

    setComplaintData: (state, action) => {
      state.complaintData = {
        ...state.complaintData,
        ...action.payload,
      };
    },

    // --------------------------------------------------
    // RISK DATA
    // --------------------------------------------------

    setRiskData: (state, action) => {
      state.riskData = {
        ...state.riskData,
        ...action.payload,
      };
    },

    // --------------------------------------------------
    // LOADING
    // --------------------------------------------------

    setLoading: (state, action) => {
      state.loading = action.payload;
    },

    // --------------------------------------------------
    // ERROR
    // --------------------------------------------------

    setError: (state, action) => {
      state.error = action.payload;
    },

    clearError: (state) => {
      state.error = null;
    },

    // --------------------------------------------------
    // STATUS
    // --------------------------------------------------

    setStatus: (state, action) => {
      state.status = action.payload;
    },

    // --------------------------------------------------
    // SELECTED PDF
    // --------------------------------------------------

    setSelectedFile: (state, action) => {
      state.selectedFile = action.payload;
    },

    // --------------------------------------------------
    // RESET EVERYTHING
    // --------------------------------------------------

    resetComplaint: (state) => {
      state.complaintData = {
        ...initialComplaintData,
      };

      state.riskData = {};
      state.loading = false;
      state.error = null;
      state.status = "PENDING_TRIAGE";
      state.selectedFile = null;
    },
  },
});

export const {
  setComplaintData,
  setRiskData,
  setLoading,
  setError,
  clearError,
  setStatus,
  setSelectedFile,
  resetComplaint,
} = complaintsSlice.actions;

export default complaintsSlice.reducer;