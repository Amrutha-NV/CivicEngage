from __future__ import annotations

from typing import List

from models.campaign import Campaign
from models.volunteer import Volunteer


class TextBuilder:
    @staticmethod
    def build_volunteer_text(volunteer: Volunteer) -> str:
        skills = ", ".join(volunteer.skills)
        availability = ", ".join(volunteer.availability)
        return (
            f"Volunteer {volunteer.name} located in {volunteer.location}, "
            f"skilled in {skills}. Availability: {availability}. "
            f"Attendance rate: {volunteer.attendance_rate:.2f}, "
            f"social impact score: {volunteer.social_impact_score:.2f}. "
            f"Verified: {volunteer.verified}."
        )

    @staticmethod
    def build_campaign_text(campaign: Campaign) -> str:
        required_skills = ", ".join(campaign.required_skills)
        return (
            f"Campaign {campaign.title} in {campaign.location} ({campaign.category}) with "
            f"description: {campaign.description}. Required skills: {required_skills}. "
            f"Maximum volunteers: {campaign.maximum_volunteers}, current volunteers: {campaign.current_volunteers}."
        )
