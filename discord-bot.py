from courselib import CourseMonitor, Term, Semester, Course

import os
from dotenv import load_dotenv

import discord
import requests

load_dotenv()
webhook_url = os.getenv("WEBHOOK_URL")


def webhook_callback(message: str):
    r = requests.post(
        webhook_url,
        json={
            "username": "Purdue Course Monitor",
            "content": message,
        },
    )

    if r.status_code != 204:
        print(f"Error sending webhook: {r.text}")


monitor = CourseMonitor("data", callback=webhook_callback, fetch_interval=60)
bot = discord.Bot()


@bot.command(description="Add a course to monitor", usage="SPRING 2024 CS 25200")
async def add_course(
    ctx,
    semester: discord.Option(str),
    year: discord.Option(str),
    subject: discord.Option(str),
    number: discord.Option(str),
):
    term = Term(year=int(year), semester=Semester(semester))

    course = Course(subject=subject, number=number, term=term)

    try:
        monitor.add_course(course)
        await ctx.respond(f"Added {course}")
    except Exception as e:
        await ctx.respond(f"Error adding course: {e}")


@bot.command(
    description="Remove a course from monitoring", usage="SPRING 2024 CS 25200"
)
async def remove_course(
    ctx,
    semester: discord.Option(str),
    year: discord.Option(str),
    subject: discord.Option(str),
    number: discord.Option(str),
):
    term = Term(year=int(year), semester=Semester(semester))

    course = Course(subject=subject, number=number, term=term)

    try:
        monitor.remove_course(course)
        await ctx.respond(f"Removed {course}")
    except Exception as e:
        await ctx.respond(f"Error removing course: {e}")


@bot.command(description="List all courses being monitored")
async def list_courses(ctx):
    courses = monitor.get_courses()

    if len(courses) == 0:
        await ctx.respond("No courses being monitored")
        return

    await ctx.respond("\n".join([str(course) for course in courses]))


bot.run(os.getenv("DISCORD_TOKEN"))
