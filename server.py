#!/usr/bin/env python3
"""
MCP Server for Project + Agentic AI API
All endpoints from OpenAPI spec
"""
import json
import sys
import os
import httpx
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://projectschool.alumnx.com"
# BASE_URL = "http://localhost:8001"  # Local testing
API_KEY = os.environ.get("PROJECT_SCHOOL_API_KEY", "")

# ============================================================================
# HTTP HELPER
# ============================================================================

async def api_request(method: str, path: str, body: dict = None, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        url = f"{BASE_URL}{path}"
        headers = {"X-API-Key": API_KEY}
        kwargs = {"headers": headers}
        if body:
            kwargs["json"] = body
        if params:
            kwargs["params"] = {k: v for k, v in params.items() if v is not None}
        response = await client.request(method, url, **kwargs)
        try:
            return response.json()
        except Exception:
            return {"status_code": response.status_code, "text": response.text}

# ============================================================================
# MCP SERVER
# ============================================================================
server = Server("project-agentic-ai-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [

        # ── GOALS ────────────────────────────────────────────────────────────
        types.Tool(
            name="goals_get_all",
            description="Get all goals, optionally filtered by userId",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "Optional user ID filter"}
                }
            }
        ),
        types.Tool(
            name="goals_set",
            description="Set or update user goals (upsert)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "goals": {"type": "string"}
                },
                "required": ["userId", "goals"]
            }
        ),
        types.Tool(
            name="goals_get_by_user",
            description="Get goals for a specific user by user_id",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="goals_manage",
            description="Create or update goals for a user (text string up to 1024 chars)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "goals": {"type": "string"}
                },
                "required": ["userId", "goals"]
            }
        ),
        types.Tool(
            name="goals_get",
            description="Get goals for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),

        # ── PROJECTS ─────────────────────────────────────────────────────────
        types.Tool(
            name="projects_list",
            description="Get all projects - admin projects and user-created projects",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "Optional user ID filter"}
                }
            }
        ),
        types.Tool(
            name="projects_create",
            description="Create a new project",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "projectType": {"type": "string", "enum": ["project", "training"]},
                    "status": {"type": "string"},
                    "createdBy": {"type": "string"}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="projects_get_details",
            description="Get project details along with all associated tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "userId": {"type": "string"}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="projects_delete",
            description="Delete a project and all associated data (tasks, assignments)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="projects_get_stats",
            description="Get statistics about tasks in a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="projects_get_tasks_assigned_to_user",
            description="Get all tasks for a project with assignment status for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectId": {"type": "string"},
                    "userId": {"type": "string"}
                },
                "required": ["projectId", "userId"]
            }
        ),

        # ── TASKS ─────────────────────────────────────────────────────────────
        types.Tool(
            name="tasks_get_all",
            description="Get all tasks, optionally filtered by project_id and userId",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "userId": {"type": "string"}
                }
            }
        ),
        types.Tool(
            name="tasks_create",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "estimatedTime": {"type": "number"},
                    "skillType": {"type": "string"},
                    "day": {"type": "string"},
                    "taskType": {"type": "string", "enum": ["Theory", "Practical"]},
                    "createdBy": {"type": "string"},
                    "isEnabled": {"type": "boolean"},
                    "isValidation": {"type": "boolean"},
                    "autoAssign": {"type": "boolean"},
                    "isGlobal": {"type": "boolean"}
                },
                "required": ["project_id", "title", "estimatedTime", "skillType"]
            }
        ),
        types.Tool(
            name="tasks_get",
            description="Get a specific task by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="tasks_update",
            description="Update a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "estimatedTime": {"type": "number"},
                    "skillType": {"type": "string"},
                    "priority": {"type": "string"},
                    "isEnabled": {"type": "boolean"},
                    "isValidation": {"type": "boolean"},
                    "day": {"type": "string"},
                    "taskType": {"type": "string", "enum": ["Theory", "Practical"]}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="tasks_delete",
            description="Delete a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="tasks_update_user_created",
            description="Update a task only if created by the specified user",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "estimatedTime": {"type": "number"},
                    "skillType": {"type": "string"},
                    "isEnabled": {"type": "boolean"},
                    "day": {"type": "string"},
                    "taskType": {"type": "string", "enum": ["Theory", "Practical"]}
                },
                "required": ["task_id", "user_id"]
            }
        ),
        types.Tool(
            name="tasks_delete_user_created",
            description="Delete a task only if created by the specified user",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "user_id": {"type": "string"}
                },
                "required": ["task_id", "user_id"]
            }
        ),
        types.Tool(
            name="tasks_link_to_user",
            description="Link a task to a user by adding it to their assignments",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "taskId": {"type": "string"},
                    "assignedBy": {"type": "string", "enum": ["user", "admin"]},
                    "sequenceId": {"type": "integer"},
                    "expectedCompletionDate": {"type": "string"},
                    "assignerUserId": {"type": "string"},
                    "assignerName": {"type": "string"},
                    "assignerEmail": {"type": "string"}
                },
                "required": ["userId", "taskId"]
            }
        ),
        types.Tool(
            name="tasks_get_user_tasks",
            description="Get all tasks assigned to a user with full task and project details",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="tasks_bulk_clear_all_users",
            description="Clear all assigned tasks for ALL users in the system",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="tasks_clear_user_tasks",
            description="Clear all assigned tasks for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="tasks_delete_and_assignments",
            description="If user is creator: delete task and remove from ALL users' assignments",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="tasks_unassign_user",
            description="Remove a task from user's assignments (unassign only, does not delete task)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="tasks_mark_complete",
            description="Mark a task as completed for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="tasks_add_comment",
            description="Add a comment to a user's task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"},
                    "comment": {"type": "string"},
                    "commentBy": {"type": "string", "enum": ["user", "admin"]}
                },
                "required": ["user_id", "task_id", "comment", "commentBy"]
            }
        ),
        types.Tool(
            name="tasks_mark_active",
            description="Mark a task as active for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="tasks_bulk_assign_to_user",
            description="Bulk assign multiple tasks to a user with their sequence IDs. Replaces all existing assignments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "taskId": {"type": "string"},
                                "sequenceId": {"type": "integer"}
                            },
                            "required": ["taskId", "sequenceId"]
                        }
                    },
                    "adminId": {"type": "string"},
                    "adminName": {"type": "string"},
                    "adminEmail": {"type": "string"}
                },
                "required": ["userId", "tasks"]
            }
        ),
        types.Tool(
            name="tasks_bulk_add_to_project",
            description="Bulk add multiple tasks to a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "projectId": {"type": "string"},
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "estimatedTime": {"type": "number"},
                                "skillType": {"type": "string"},
                                "isEnabled": {"type": "boolean"},
                                "isValidation": {"type": "boolean"},
                                "day": {"type": "string"},
                                "taskType": {"type": "string", "enum": ["Theory", "Practical"]}
                            },
                            "required": ["title", "estimatedTime", "skillType"]
                        }
                    }
                },
                "required": ["projectId", "tasks"]
            }
        ),
        types.Tool(
            name="tasks_flush_by_category",
            description="Delete all tasks in a project for a specific category (skillType)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "skill_type": {"type": "string"}
                },
                "required": ["project_id", "skill_type"]
            }
        ),
        types.Tool(
            name="tasks_broadcast",
            description="Broadcast a task to specific users or ALL users in the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "taskId": {"type": "string"},
                    "userIds": {"type": "array", "items": {"type": "string"}},
                    "broadcastToAll": {"type": "boolean"},
                    "adminId": {"type": "string"},
                    "adminName": {"type": "string"},
                    "adminEmail": {"type": "string"}
                },
                "required": ["taskId"]
            }
        ),
        types.Tool(
            name="tasks_sync_admin_tasks",
            description="Assign all existing admin/system-created tasks to a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="tasks_trigger_email",
            description="Trigger a templated email with user task progress stats",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="tasks_send_custom_email",
            description="Send a custom templated email directly via ZeptoMail",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "message": {"type": "string"},
                    "userName": {"type": "string"},
                    "userEmail": {"type": "string"}
                },
                "required": ["userId", "message"]
            }
        ),

        # ── CHAT ─────────────────────────────────────────────────────────────
        types.Tool(
            name="chat_with_agent",
            description="Invoke the learning agent for a user with optional message or resume data",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "message": {"type": "string"},
                    "resumeData": {"type": "object"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="chat_get_history",
            description="Retrieve chat history for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="chat_clear_history",
            description="Clear all chat history for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="chat_manage_agent",
            description="Create or update agent name for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "agentName": {"type": "string"}
                },
                "required": ["userId", "agentName"]
            }
        ),
        types.Tool(
            name="chat_get_agent",
            description="Get agent details for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="chat_agent_conversation",
            description="Check for active tasks due today and send WhatsApp reminders",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),

        # ── ASSIGNED PROJECTS ─────────────────────────────────────────────────
        types.Tool(
            name="assigned_projects_assign",
            description="Assign projects to a user. Replaces all existing project assignments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "projects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "projectId": {"type": "string"},
                                "sequenceId": {"type": "integer"}
                            },
                            "required": ["projectId", "sequenceId"]
                        }
                    }
                },
                "required": ["userId", "projects"]
            }
        ),

        # ── PREFERENCES ───────────────────────────────────────────────────────
        types.Tool(
            name="preferences_manage",
            description="Create or update preferences for a user (list of strings)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "preferences": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["userId", "preferences"]
            }
        ),
        types.Tool(
            name="preferences_get",
            description="Get preferences for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),

        # ── QUIZZES ───────────────────────────────────────────────────────────
        types.Tool(
            name="quizzes_get_by_task",
            description="Get the quiz associated with a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="quizzes_create_or_update",
            description="Create or update a quiz for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "taskId": {"type": "string"},
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "options": {"type": "array", "items": {"type": "string"}},
                                "correctAnswer": {"type": "string"},
                                "explanation": {"type": "string"}
                            },
                            "required": ["question", "options", "correctAnswer", "explanation"]
                        }
                    }
                },
                "required": ["taskId", "questions"]
            }
        ),

        # ── ASSESSMENTS ───────────────────────────────────────────────────────
        types.Tool(
            name="assessments_run",
            description="Run an assessment for a task against a student's endpoint URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "taskId": {"type": "string"},
                    "studentUrl": {"type": "string"}
                },
                "required": ["taskId", "studentUrl"]
            }
        ),
        types.Tool(
            name="assessments_get_history",
            description="Get assessment history for a task and user",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "user_id": {"type": "string"}
                },
                "required": ["task_id", "user_id"]
            }
        ),

        # ── PROJECT SCHOOL ────────────────────────────────────────────────────
        types.Tool(
            name="projectschool_debug_tasks",
            description="Debug tasks endpoint for Project School",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="projectschool_reports_login",
            description="Login for Reports Admin (uses Main DB Users)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userName": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["userName", "password"]
            }
        ),
        types.Tool(
            name="projectschool_get_projects",
            description="Fetch all projects from Agriculture DB",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="projectschool_get_cohort_members",
            description="Get all cohort members",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="projectschool_create_task",
            description="Create a new global task template for Project School broadcasting",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "title": {"type": "string"},
                    "estimatedTime": {"type": "number"},
                    "skillType": {"type": "string"},
                    "description": {"type": "string"},
                    "isGlobal": {"type": "boolean"},
                    "taskType": {"type": "string", "enum": ["Theory", "Practical"]}
                },
                "required": ["project_id", "title", "estimatedTime", "skillType"]
            }
        ),
        types.Tool(
            name="projectschool_broadcast_task",
            description="Link a task ID to multiple users at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "taskId": {"type": "string"},
                    "adminId": {"type": "string"},
                    "adminName": {"type": "string"},
                    "adminEmail": {"type": "string"},
                    "userIds": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["taskId", "adminId", "userIds"]
            }
        ),
        types.Tool(
            name="projectschool_fetch_feedback",
            description="Fetch feedback for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="projectschool_fetch_user_assignments",
            description="Fetch assignments for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="projectschool_complete_task",
            description="Proxy to mark a task as complete",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "taskId": {"type": "string"}
                },
                "required": ["userId", "taskId"]
            }
        ),
        types.Tool(
            name="projectschool_link_task_to_user",
            description="Proxy to link a task to a user (compatible with frontend path)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId":         {"type": "string"},
                    "taskId":         {"type": "string"},
                    "assignerUserId": {"type": "string"},
                    "assignerName":   {"type": "string"},
                    "assignerEmail":  {"type": "string"}
                },
                "required": ["userId", "taskId"]
            }
        ),
        types.Tool(
            name="projectschool_mark_task_active",
            description="Proxy to make a task active for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "task_id": {"type": "string"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="projectschool_add_assignment",
            description="Add an assignment template",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["name"]
                        }
                    },
                    "isGlobal": {"type": "boolean"},
                    "createdBy": {"type": "string"}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="projectschool_add_feedback",
            description="Add feedback for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "message": {"type": "string"},
                    "adminId": {"type": "string"}
                },
                "required": ["userId", "message", "adminId"]
            }
        ),
        types.Tool(
            name="projectschool_get_assignments",
            description="Get all assignments",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="projectschool_update_assignment",
            description="Update an assignment",
            inputSchema={
                "type": "object",
                "properties": {
                    "assignmentId": {"type": "string"}
                },
                "required": ["assignmentId"]
            }
        ),
        types.Tool(
            name="projectschool_delete_assignment",
            description="Delete an assignment",
            inputSchema={
                "type": "object",
                "properties": {
                    "assignmentId": {"type": "string"}
                },
                "required": ["assignmentId"]
            }
        ),
        types.Tool(
            name="projectschool_get_preferences",
            description="Get preferences for a user (Project School proxy)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="projectschool_get_dashboard_stats",
            description="Get dashboard stats for a user (XP, streaks, skills)",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        ),
        types.Tool(
            name="projectschool_log_activity",
            description="Update XP and Streak when a task is completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"},
                    "taskId": {"type": "string"}
                },
                "required": ["userId", "taskId"]
            }
        ),

        # ── HEALTH ─────────────────────────────────────────────────────────────
        types.Tool(
            name="health_check",
            description="Check API health status",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_current_user",
            description="Get the currently logged in user's ID and name",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    args = arguments or {}

    try:
        # ── GOALS ────────────────────────────────────────────────────────────
        if name == "goals_get_all":
            result = await api_request("GET", "/goals/", params={"userId": args.get("userId")})

        elif name == "goals_set":
            result = await api_request("POST", "/goals/", body={"userId": args["userId"], "goals": args["goals"]})

        elif name == "goals_get_by_user":
            result = await api_request("GET", f"/goals/{args['user_id']}")

        elif name == "goals_manage":
            result = await api_request("POST", "/goals/manage-goals", body={"userId": args["userId"], "goals": args["goals"]})

        elif name == "goals_get":
            result = await api_request("POST", "/goals/get-goals", body={"userId": args["userId"]})

        # ── PROJECTS ─────────────────────────────────────────────────────────
        elif name == "projects_list":
            result = await api_request("GET", "/projects/", params={"userId": args.get("userId")})

        elif name == "projects_create":
            result = await api_request("POST", "/projects/", body=args)

        elif name == "projects_get_details":
            result = await api_request("GET", f"/projects/{args['project_id']}", params={"userId": args.get("userId")})

        elif name == "projects_delete":
            result = await api_request("DELETE", f"/projects/{args['project_id']}")

        elif name == "projects_get_stats":
            result = await api_request("GET", f"/projects/{args['project_id']}/stats")

        elif name == "projects_get_tasks_assigned_to_user":
            result = await api_request("POST", "/projects/get-project-tasks-assigned-to-user", body={"projectId": args["projectId"], "userId": args["userId"]})

        # ── TASKS ─────────────────────────────────────────────────────────────
        elif name == "tasks_get_all":
            result = await api_request("GET", "/tasks/", params={"project_id": args.get("project_id"), "userId": args.get("userId")})

        elif name == "tasks_create":
            result = await api_request("POST", "/tasks/", body=args)

        elif name == "tasks_get":
            result = await api_request("GET", f"/tasks/{args['task_id']}")

        elif name == "tasks_update":
            task_id = args.pop("task_id")
            result = await api_request("PUT", f"/tasks/{task_id}", body=args)

        elif name == "tasks_delete":
            result = await api_request("DELETE", f"/tasks/{args['task_id']}")

        elif name == "tasks_update_user_created":
            task_id = args.pop("task_id")
            user_id = args.pop("user_id")
            result = await api_request("PUT", f"/tasks/{task_id}/user/{user_id}", body=args)

        elif name == "tasks_delete_user_created":
            result = await api_request("DELETE", f"/tasks/{args['task_id']}/user/{args['user_id']}")

        elif name == "tasks_link_to_user":
            result = await api_request("POST", "/tasks/link-user-task", body=args)

        elif name == "tasks_get_user_tasks":
            result = await api_request("GET", f"/tasks/user-tasks/{args['user_id']}")

        elif name == "tasks_bulk_clear_all_users":
            result = await api_request("DELETE", "/tasks/user-tasks/bulk-clear-all-users")

        elif name == "tasks_clear_user_tasks":
            result = await api_request("DELETE", f"/tasks/user-tasks/{args['user_id']}/clear")

        elif name == "tasks_delete_and_assignments":
            result = await api_request("DELETE", f"/tasks/user-tasks/{args['user_id']}/{args['task_id']}")

        elif name == "tasks_unassign_user":
            result = await api_request("DELETE", f"/tasks/task/user-task/{args['user_id']}/unassign/{args['task_id']}")

        elif name == "tasks_mark_complete":
            result = await api_request("PUT", f"/tasks/user-tasks/{args['user_id']}/{args['task_id']}/complete")

        elif name == "tasks_add_comment":
            from datetime import datetime, timezone
            result = await api_request("PUT", f"/tasks/user-tasks/{args['user_id']}/{args['task_id']}/comment",
                body={"comment": args["comment"], "commentBy": args["commentBy"], "createdAt": datetime.now(timezone.utc).isoformat()})

        elif name == "tasks_mark_active":
            result = await api_request("PUT", f"/tasks/user-tasks/{args['user_id']}/{args['task_id']}/active")

        elif name == "tasks_bulk_assign_to_user":
            result = await api_request("POST", "/tasks/bulk-assign-tasks-to-user", body=args)

        elif name == "tasks_bulk_add_to_project":
            result = await api_request("POST", "/tasks/bulk-add-tasks-to-project", body=args)

        elif name == "tasks_flush_by_category":
            result = await api_request("DELETE", f"/tasks/project/{args['project_id']}/category/{args['skill_type']}")

        elif name == "tasks_broadcast":
            result = await api_request("POST", "/tasks/broadcast-task", body=args)

        elif name == "tasks_sync_admin_tasks":
            result = await api_request("POST", f"/tasks/sync-admin-tasks/{args['user_id']}")

        elif name == "tasks_trigger_email":
            result = await api_request("POST", "/tasks/trigger-email", body={"userId": args["userId"]})

        elif name == "tasks_send_custom_email":
            result = await api_request("POST", "/tasks/send-custom-email", body=args)

        # ── CHAT ─────────────────────────────────────────────────────────────
        elif name == "chat_with_agent":
            result = await api_request("POST", "/chat/agent", body=args)

        elif name == "chat_get_history":
            result = await api_request("GET", f"/chat/history/{args['user_id']}")

        elif name == "chat_clear_history":
            result = await api_request("DELETE", f"/chat/clear-history/{args['user_id']}")

        elif name == "chat_manage_agent":
            result = await api_request("POST", "/chat/manage-agent", body=args)

        elif name == "chat_get_agent":
            result = await api_request("POST", "/chat/get-agent", body={"userId": args["userId"]})

        elif name == "chat_agent_conversation":
            result = await api_request("POST", "/chat/agent/conversation", body=args)

        # ── ASSIGNED PROJECTS ─────────────────────────────────────────────────
        elif name == "assigned_projects_assign":
            result = await api_request("POST", "/assignedprojects/assign-projects", body=args)

        # ── PREFERENCES ───────────────────────────────────────────────────────
        elif name == "preferences_manage":
            result = await api_request("POST", "/preferences/manage-preferences", body=args)

        elif name == "preferences_get":
            result = await api_request("POST", "/preferences/get-preferences", body={"userId": args["userId"]})

        # ── QUIZZES ───────────────────────────────────────────────────────────
        elif name == "quizzes_get_by_task":
            result = await api_request("GET", f"/quizzes/task/{args['task_id']}")

        elif name == "quizzes_create_or_update":
            result = await api_request("POST", "/quizzes/", body=args)

        # ── ASSESSMENTS ───────────────────────────────────────────────────────
        elif name == "assessments_run":
            result = await api_request("POST", "/assessments/run", body=args)

        elif name == "assessments_get_history":
            result = await api_request("GET", f"/assessments/history/{args['task_id']}/{args['user_id']}")

        # ── PROJECT SCHOOL ────────────────────────────────────────────────────
        elif name == "projectschool_debug_tasks":
            result = await api_request("GET", "/api/projectschool/debug/tasks")

        elif name == "projectschool_reports_login":
            result = await api_request("POST", "/api/projectschool/reports-login", body=args)

        elif name == "projectschool_get_projects":
            result = await api_request("GET", "/api/projectschool/projects")

        elif name == "projectschool_get_cohort_members":
            result = await api_request("GET", "/api/projectschool/get-cohort-members")

        elif name == "projectschool_create_task":
            result = await api_request("POST", "/api/projectschool/tasks", body=args)

        elif name == "projectschool_broadcast_task":
            result = await api_request("POST", "/api/projectschool/tasks/broadcast-task", body=args)

        elif name == "projectschool_fetch_feedback":
            result = await api_request("POST", "/api/projectschool/feedback/fetch", body=args)

        elif name == "projectschool_fetch_user_assignments":
            result = await api_request("POST", "/api/projectschool/assignments/user/assignments", body=args)

        elif name == "projectschool_complete_task":
            result = await api_request("POST", "/api/projectschool/assignments/user/complete-task", body=args)

        elif name == "projectschool_link_task_to_user":
            result = await api_request("POST", "/api/projectschool/tasks/link-user-task", body=args)

        elif name == "projectschool_mark_task_active":
            result = await api_request("PUT", f"/api/projectschool/tasks/user-tasks/{args['user_id']}/{args['task_id']}/active")

        elif name == "projectschool_add_assignment":
            result = await api_request("POST", "/api/projectschool/add-assignment", body=args)

        elif name == "projectschool_add_feedback":
            result = await api_request("POST", "/api/projectschool/feedback", body=args)

        elif name == "projectschool_get_assignments":
            result = await api_request("GET", "/api/projectschool/get-assignments")

        elif name == "projectschool_update_assignment":
            result = await api_request("POST", "/api/projectschool/update-assignment", body=args)

        elif name == "projectschool_delete_assignment":
            result = await api_request("POST", "/api/projectschool/assignments/delete", body=args)

        elif name == "projectschool_get_preferences":
            result = await api_request("POST", "/api/projectschool/get-preferences", body=args)

        elif name == "projectschool_get_dashboard_stats":
            result = await api_request("GET", f"/api/projectschool/dashboard-stats/{args['userId']}")

        elif name == "projectschool_log_activity":
            result = await api_request("POST", "/api/projectschool/log-activity", body=args)
        elif name == "get_current_user":
            result = {
                "userId":    os.environ.get("CURRENT_USER_ID", ""),
                "userName":  os.environ.get("CURRENT_USER_NAME", ""),
                "userEmail": os.environ.get("CURRENT_USER_EMAIL", "")
            }
        # ── HEALTH ─────────────────────────────────────────────────────────────
        elif name == "health_check":
            result = await api_request("GET", "/health")

        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    print("🚀 Starting Project+Agentic AI MCP Server...", file=sys.stderr)
    print(f"🔑 API Key loaded: {'✅ Yes' if API_KEY else '❌ Missing - add PROJECT_SCHOOL_API_KEY to config'}", file=sys.stderr)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="project-agentic-ai-mcp-server",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
        )
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    import asyncio
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    asyncio.run(main())
