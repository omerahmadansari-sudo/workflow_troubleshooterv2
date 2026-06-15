from typing import Dict, List, Optional, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(
    title="Support Troubleshoot Wizard",
    description="English-only troubleshooting API for GHL support issues",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


IssueType = Literal["workflow_not_firing", "email_sms_not_sending", "calendar_issue"]


class OptionItem(BaseModel):
    value: str
    label: str


class QuestionItem(BaseModel):
    id: str
    text: str
    type: str
    required: bool
    options: Optional[List[OptionItem]] = None


class IssueQuestionsResponse(BaseModel):
    issue_type: str
    label: str
    questions: List[QuestionItem]


class DiagnoseRequest(BaseModel):
    issue_type: IssueType
    answers: Dict[str, str]


class DiagnosisDetail(BaseModel):
    code: str
    title: str
    confidence: str
    severity: str
    why: List[str]
    fix_steps: List[str]
    retest_steps: List[str]


class SecondaryCause(BaseModel):
    code: str
    title: str
    hint: str


class DiagnoseResponse(BaseModel):
    issue_type: str
    primary_diagnosis: DiagnosisDetail
    secondary_causes: List[SecondaryCause]
    report_text: str


SUPPORT_ISSUES = [
    {"issue_type": "workflow_not_firing", "label": "Workflow not firing"},
    {"issue_type": "email_sms_not_sending", "label": "Email/SMS not sending"},
    {"issue_type": "calendar_issue", "label": "Calendar booking issue"},
]


SUPPORT_QUESTIONS: Dict[str, Dict] = {
    "workflow_not_firing": {
        "issue_type": "workflow_not_firing",
        "label": "Workflow not firing",
        "questions": [
            {
                "id": "workflow_active",
                "text": "Is the workflow currently live/published (not draft)?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "trigger_type",
                "text": "What event should start this workflow?",
                "type": "single_choice",
                "required": True,
                "options": [
                    {"value": "form_submitted", "label": "Form submitted"},
                    {"value": "tag_added", "label": "Tag added"},
                    {"value": "opportunity_changed", "label": "Opportunity stage/field changed"},
                    {"value": "appointment_booked", "label": "Appointment booked"},
                    {"value": "contact_created", "label": "Contact created"},
                    {"value": "other", "label": "Something else"},
                ],
            },
            {
                "id": "event_happened",
                "text": "Did this event definitely happen on the test contact?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "used_real_contact",
                "text": "Did you test with a real contact record (not preview/test-only)?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "has_filters",
                "text": "Does the workflow have filters/conditions on who can enter?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "tag_used_in_trigger",
                "text": "Are you using tags in the trigger or filters?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "tag_confirmed",
                "text": "If tags are used, is the correct tag actually being applied to the contact?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "other_workflows_exist",
                "text": "Do you have any other workflows that could update the same contact or tags?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "worked_before",
                "text": "Has this workflow ever worked before?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "recent_changes",
                "text": "Did the problem start right after you changed this workflow?",
                "type": "boolean",
                "required": False,
            },
        ],
    },
    "email_sms_not_sending": {
        "issue_type": "email_sms_not_sending",
        "label": "Email/SMS not sending",
        "questions": [
            {
                "id": "channel",
                "text": "Which channel is failing?",
                "type": "single_choice",
                "required": True,
                "options": [
                    {"value": "email", "label": "Email"},
                    {"value": "sms", "label": "SMS"},
                    {"value": "both", "label": "Both email and SMS"},
                ],
            },
            {
                "id": "workflow_live",
                "text": "Is the workflow or campaign set to live/active?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "template_selected",
                "text": "Is there a real email/SMS template selected in the action (not blank or draft)?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "sender_connected",
                "text": "Is your email domain / phone number connected and verified?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "channel_worked_before",
                "text": "Has this channel worked before in this sub-account?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "contact_opted_in",
                "text": "Is the contact opted in for this channel (not unsubscribed/blocked)?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "has_sms_credits",
                "text": "For SMS, do you have credits / an active SMS sending setup?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "uses_delays_windows",
                "text": "Does the workflow use delays or specific sending windows (days/times)?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "contact_reached_step",
                "text": "Can you see that the contact reached the email/SMS step in the workflow history?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "multiple_automations",
                "text": "Are there other workflows or campaigns that could send or stop similar messages?",
                "type": "boolean",
                "required": False,
            },
        ],
    },
    "calendar_issue": {
        "issue_type": "calendar_issue",
        "label": "Calendar booking issue",
        "questions": [
            {
                "id": "calendar_symptom",
                "text": "What’s going wrong with the calendar?",
                "type": "single_choice",
                "required": True,
                "options": [
                    {"value": "no_slots", "label": "No time slots are visible"},
                    {"value": "booking_fails", "label": "Booking fails or errors after form submit"},
                    {"value": "no_confirmation", "label": "Booking works but the client gets no confirmation"},
                    {"value": "wrong_user", "label": "Bookings are assigned to the wrong user"},
                    {"value": "double_booking", "label": "Double bookings or wrong availability"},
                ],
            },
            {
                "id": "calendar_connected",
                "text": "Is the calendar connected to the correct user/team?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "availability_set",
                "text": "Does this calendar have at least one availability window set?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "timezone_correct",
                "text": "Is the timezone set correctly for the calendar?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "uses_form_handoff",
                "text": "Does a form need to be submitted before the booking happens?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "form_submits_ok",
                "text": "Does the lead successfully submit the form (no errors)?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "round_robin",
                "text": "Is round-robin or any advanced routing turned on for this calendar?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "booking_visible_in_calendar",
                "text": "When you test, does the booking appear in the calendar at all?",
                "type": "boolean",
                "required": True,
            },
            {
                "id": "calendar_worked_before",
                "text": "Has this calendar worked correctly before?",
                "type": "boolean",
                "required": False,
            },
            {
                "id": "calendar_recent_changes",
                "text": "Did you change any calendar or workflow settings just before it broke?",
                "type": "boolean",
                "required": False,
            },
        ],
    },
}


DIAGNOSIS_LIBRARY = {
    "workflow_inactive": {
        "title": "Workflow is not live",
        "severity": "critical",
        "why": [
            "The workflow appears to be inactive or still in draft mode.",
            "Inactive workflows cannot enroll new contacts.",
        ],
        "fix_steps": [
            "Open the workflow in your CRM.",
            "Change its status to live/published.",
            "Save the workflow.",
            "Retest with a fresh contact and the same trigger event.",
        ],
        "retest_steps": [
            "Create a new test contact.",
            "Trigger the same event again.",
            "Check whether the contact enters the workflow history.",
        ],
        "hint": "Check workflow status first.",
    },
    "trigger_event_missing": {
        "title": "The trigger event did not happen",
        "severity": "critical",
        "why": [
            "The workflow can only start if the trigger event actually occurs.",
            "If the event never happens, the contact will never enroll.",
        ],
        "fix_steps": [
            "Confirm exactly which event should start the workflow.",
            "Test again with a fresh contact.",
            "Make sure the expected trigger action really happens.",
        ],
        "retest_steps": [
            "Repeat the trigger event with a new contact.",
            "Check enrollment history after the event.",
        ],
        "hint": "Recreate the event with a fresh test contact.",
    },
    "trigger_conditions_not_met": {
        "title": "Trigger conditions are not being met",
        "severity": "moderate",
        "why": [
            "The workflow has filters or entry conditions.",
            "One or more of those conditions may not match the contact.",
        ],
        "fix_steps": [
            "Open the workflow trigger and review all filters.",
            "Check the test contact’s fields, tags, and values.",
            "Temporarily simplify the trigger and test again.",
        ],
        "retest_steps": [
            "Run the test again after simplifying the conditions.",
            "Compare the contact record to the trigger filters.",
        ],
        "hint": "Simplify filters and test again.",
    },
    "wrong_field_or_tag": {
        "title": "Wrong tag or field is being watched",
        "severity": "moderate",
        "why": [
            "The workflow depends on a tag or field value to start.",
            "That tag or field may not be the one actually being updated.",
        ],
        "fix_steps": [
            "Check the exact tag/field used in the trigger.",
            "Confirm the same tag/field is being updated on the contact.",
            "Correct the trigger if the wrong item is selected.",
        ],
        "retest_steps": [
            "Apply the exact tag or update the exact field again.",
            "Watch whether the contact enrolls.",
        ],
        "hint": "Match the trigger tag/field to the real contact update.",
    },
    "conflicting_automation": {
        "title": "Another workflow may be conflicting",
        "severity": "moderate",
        "why": [
            "Other workflows can update the same contact, tags, or fields.",
            "That can create conflicts or remove the condition needed for enrollment.",
        ],
        "fix_steps": [
            "Review other workflows touching the same contact data.",
            "Temporarily pause related workflows.",
            "Retest the primary workflow by itself.",
        ],
        "retest_steps": [
            "Disable other related automations temporarily.",
            "Run the same test again.",
        ],
        "hint": "Look for tag removals or field changes by other workflows.",
    },
    "workflow_recent_change_breakage": {
        "title": "Recent changes likely broke the workflow",
        "severity": "moderate",
        "why": [
            "The issue started after recent edits.",
            "A changed trigger, condition, or step may have broken the setup.",
        ],
        "fix_steps": [
            "Review the workflow changes you made most recently.",
            "Compare the current setup to the last working version.",
            "Undo the suspected change and retest.",
        ],
        "retest_steps": [
            "Retest after reverting the recent change.",
            "Check whether new contacts now enroll.",
        ],
        "hint": "Recent edits are the strongest clue here.",
    },
    "campaign_inactive": {
        "title": "The campaign or workflow is not live",
        "severity": "critical",
        "why": [
            "An inactive campaign or workflow cannot send messages.",
            "The send step will never execute until it is live.",
        ],
        "fix_steps": [
            "Open the workflow or campaign.",
            "Set it to live/active.",
            "Save changes and retest.",
        ],
        "retest_steps": [
            "Use a fresh test contact.",
            "Trigger the send again and verify delivery.",
        ],
        "hint": "Check active status first.",
    },
    "missing_template": {
        "title": "The message template is missing or incomplete",
        "severity": "critical",
        "why": [
            "A send step needs a valid email or SMS message configured.",
            "Blank or incomplete message actions can stop delivery.",
        ],
        "fix_steps": [
            "Open the send step.",
            "Select or create the correct email/SMS template.",
            "Save the action and retest.",
        ],
        "retest_steps": [
            "Trigger the workflow again with a test contact.",
            "Confirm the contact reaches the send step.",
        ],
        "hint": "Make sure the send action has a real message selected.",
    },
    "sender_not_connected": {
        "title": "Sender account is not connected or verified",
        "severity": "critical",
        "why": [
            "Email and SMS sending depend on a valid sender setup.",
            "Disconnected or unverified sender settings can block delivery.",
        ],
        "fix_steps": [
            "Check your email domain or phone number connection.",
            "Reconnect or verify the sender setup.",
            "Retest sending after confirmation.",
        ],
        "retest_steps": [
            "Send to a test contact after reconnecting.",
            "Confirm whether delivery starts working.",
        ],
        "hint": "Check domain, mailbox, or phone setup.",
    },
    "contact_opted_out": {
        "title": "The contact is opted out or blocked",
        "severity": "moderate",
        "why": [
            "Contacts who are unsubscribed or blocked may not receive messages.",
            "Consent status can prevent the send step from working.",
        ],
        "fix_steps": [
            "Open the contact record.",
            "Check opt-in / unsubscribe status.",
            "Use a valid test contact with correct consent.",
        ],
        "retest_steps": [
            "Retest with a contact who is opted in.",
            "Confirm message delivery.",
        ],
        "hint": "Use a clean opted-in test contact.",
    },
    "sms_setup_or_credits_missing": {
        "title": "SMS setup or credits are missing",
        "severity": "critical",
        "why": [
            "SMS sending depends on an active SMS setup and available credits or configured service.",
            "Without that setup, messages cannot go out.",
        ],
        "fix_steps": [
            "Check your SMS service setup.",
            "Confirm billing, credits, or phone provisioning are active.",
            "Retest SMS after setup is complete.",
        ],
        "retest_steps": [
            "Send to a test contact after confirming SMS setup.",
            "Verify delivery or send logs.",
        ],
        "hint": "Only applies to SMS.",
    },
    "sending_window_blocking": {
        "title": "Delays or sending windows are blocking delivery",
        "severity": "moderate",
        "why": [
            "The workflow may use delays, schedules, or send windows.",
            "That can make a message appear not to send immediately.",
        ],
        "fix_steps": [
            "Review all delays and schedule windows in the workflow.",
            "Temporarily simplify timing rules.",
            "Retest during an allowed sending time.",
        ],
        "retest_steps": [
            "Retest with delays removed or reduced.",
            "Check if the message is then sent.",
        ],
        "hint": "Check timing rules and allowed windows.",
    },
    "message_step_never_reached": {
        "title": "The contact never reached the send step",
        "severity": "critical",
        "why": [
            "If the contact does not reach the email/SMS action, nothing will send.",
            "The issue may be earlier in the workflow.",
        ],
        "fix_steps": [
            "Review the workflow path before the send step.",
            "Check for conditions, waits, and branches preventing progress.",
            "Retest using a simpler path.",
        ],
        "retest_steps": [
            "Watch the contact’s workflow history.",
            "Confirm whether the send step is reached.",
        ],
        "hint": "Check earlier workflow branches first.",
    },
    "duplicate_or_conflicting_automation": {
        "title": "Another automation may be interfering",
        "severity": "moderate",
        "why": [
            "Multiple automations can send, stop, or alter message flow.",
            "That can create duplicate or blocked messaging behavior.",
        ],
        "fix_steps": [
            "Review all workflows and campaigns touching the same audience.",
            "Temporarily disable similar automations.",
            "Retest the message flow alone.",
        ],
        "retest_steps": [
            "Retest after pausing related workflows.",
            "Watch send logs and workflow history.",
        ],
        "hint": "Look for overlapping campaigns.",
    },
    "no_availability": {
        "title": "No availability is configured",
        "severity": "critical",
        "why": [
            "If no available time windows exist, clients will not see slots.",
            "The calendar needs active availability to accept bookings.",
        ],
        "fix_steps": [
            "Open the calendar settings.",
            "Add or correct availability windows.",
            "Save changes and test again.",
        ],
        "retest_steps": [
            "Open the booking page again.",
            "Check whether time slots now appear.",
        ],
        "hint": "No slots usually means no availability.",
    },
    "wrong_calendar_assignment": {
        "title": "The wrong calendar or user is assigned",
        "severity": "critical",
        "why": [
            "The calendar may be connected to the wrong user or team.",
            "That can stop booking or route meetings to the wrong person.",
        ],
        "fix_steps": [
            "Check which user/team owns the calendar.",
            "Correct the assignment or routing.",
            "Retest booking.",
        ],
        "retest_steps": [
            "Create a fresh test booking.",
            "Confirm it appears under the correct user.",
        ],
        "hint": "Check calendar ownership and routing.",
    },
    "timezone_issue": {
        "title": "Timezone settings are causing booking problems",
        "severity": "moderate",
        "why": [
            "Wrong timezone settings can hide slots or create incorrect booking times.",
            "This often looks like missing or wrong availability.",
        ],
        "fix_steps": [
            "Review the calendar timezone.",
            "Confirm user timezone and booking page timezone are correct.",
            "Retest after updating.",
        ],
        "retest_steps": [
            "View the calendar again after the timezone fix.",
            "Confirm slots and booking times are correct.",
        ],
        "hint": "Timezone mismatches can make valid slots disappear.",
    },
    "form_handoff_failed": {
        "title": "The form-to-calendar handoff is failing",
        "severity": "critical",
        "why": [
            "The lead may not be reaching the booking step after the form.",
            "A broken form handoff can stop booking completely.",
        ],
        "fix_steps": [
            "Test the form submission separately.",
            "Confirm the next step sends the lead into the booking flow.",
            "Fix any form errors or missing mappings.",
        ],
        "retest_steps": [
            "Submit the form again with a new lead.",
            "Check whether the booking step opens correctly.",
        ],
        "hint": "Start by testing the form alone.",
    },
    "confirmation_workflow_broken": {
        "title": "Booking works, but confirmation automation is broken",
        "severity": "moderate",
        "why": [
            "The booking may be successful, but the follow-up automation is failing.",
            "That usually affects confirmations, reminders, or notifications.",
        ],
        "fix_steps": [
            "Check the confirmation workflow tied to booking.",
            "Verify message steps, sender setup, and trigger conditions.",
            "Retest booking confirmation.",
        ],
        "retest_steps": [
            "Create a test booking.",
            "Check if confirmations are now sent.",
        ],
        "hint": "Booking may be fine; the follow-up may be the real issue.",
    },
    "routing_logic_issue": {
        "title": "Round-robin or routing logic is misconfigured",
        "severity": "moderate",
        "why": [
            "Advanced routing can assign bookings incorrectly or cause conflicts.",
            "That often leads to wrong user assignment or booking failures.",
        ],
        "fix_steps": [
            "Review round-robin and assignment rules.",
            "Simplify routing temporarily.",
            "Retest a booking.",
        ],
        "retest_steps": [
            "Book again with simplified routing.",
            "Confirm correct assignment.",
        ],
        "hint": "Temporarily remove complex routing to isolate the issue.",
    },
}


def yes_no(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    value = str(value).strip().lower()
    if value in {"yes", "true", "1"}:
        return True
    if value in {"no", "false", "0"}:
        return False
    return None


def build_support_questions(issue_type: str) -> IssueQuestionsResponse:
    if issue_type not in SUPPORT_QUESTIONS:
        raise HTTPException(status_code=404, detail="Unknown issue type")
    item = SUPPORT_QUESTIONS[issue_type]
    questions = [QuestionItem(**q) for q in item["questions"]]
    return IssueQuestionsResponse(
        issue_type=item["issue_type"],
        label=item["label"],
        questions=questions,
    )


def get_scores_for_workflow(answers: Dict[str, str]) -> Dict[str, int]:
    scores = {
        "workflow_inactive": 0,
        "trigger_event_missing": 0,
        "trigger_conditions_not_met": 0,
        "wrong_field_or_tag": 0,
        "conflicting_automation": 0,
        "workflow_recent_change_breakage": 0,
    }

    
