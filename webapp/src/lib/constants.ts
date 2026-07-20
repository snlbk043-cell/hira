export const DEPARTMENTS = [
  "Production", "Maintenance", "Quality", "Warehouse", "Logistics",
  "Engineering", "Projects", "Construction", "Contractor", "Admin", "Safety", "Operations",
];

export const MONTH_NAMES = [
  "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",
];

export const INCIDENT_CLASSIFICATIONS = [
  "Near Miss", "First Aid", "Medical Treatment", "Restricted Work", "Lost Time Injury", "Fatality",
];

export const RECORDABLE_CLASSIFICATIONS = [
  "Medical Treatment", "Restricted Work", "Lost Time Injury", "Fatality",
];

export const BODY_PARTS = [
  "Head", "Eye", "Hand/Finger", "Arm", "Foot/Leg", "Back", "Torso", "Multiple",
];

export const RISK_LEVELS = ["Critical", "High", "Medium", "Low"];

export const TRAINING_STATUSES = ["Completed", "In Progress", "Scheduled"];
export const OBS_STATUSES = ["Completed", "In Progress", "Pending", "Overdue"];
export const INSPECTION_STATUSES = ["Completed", "In Progress", "Pending", "Overdue"];
export const WALKTHROUGH_STATUSES = ["Completed", "In Progress", "Overdue", "Pending"];
export const CA_STATUSES = ["Completed", "In Progress", "Overdue", "Pending", "Cancelled"];
export const PTW_VERDICTS = ["Compliant", "Non-Compliant", "Partially Compliant"];
export const JSA_APPROVAL_STATUSES = ["Approved", "Pending Review", "Revision Required", "Rejected"];

export const CLOSED_LIKE = new Set(["Completed", "Compliant", "Approved", "Closed"]);
