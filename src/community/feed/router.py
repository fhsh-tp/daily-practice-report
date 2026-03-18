"""Community feed router."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from community.feed.models import FeedPost, Reaction
from core.auth.deps import get_current_user
from core.auth.permissions import MANAGE_CLASS
from core.classes.models import ClassMembership
from core.users.models import User
from shared.webpage import webpage

router = APIRouter(tags=["feed"])


async def _assert_member(class_id: str, user_id: str) -> None:
    membership = await ClassMembership.find_one(
        ClassMembership.class_id == class_id,
        ClassMembership.user_id == user_id,
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a class member")


class ShareRequest(BaseModel):
    submission_id: str
    content_preview: str = ""


class ReactionRequest(BaseModel):
    emoji: str = "👍"


@router.post("/classes/{class_id}/feed", status_code=status.HTTP_201_CREATED)
async def share_to_feed(
    class_id: str,
    body: ShareRequest,
    user: User = Depends(get_current_user),
):
    await _assert_member(class_id, str(user.id))

    # Verify the submission belongs to this student and class
    from tasks.submissions.models import TaskSubmission
    sub = await TaskSubmission.get(body.submission_id)
    if sub is None or sub.student_id != str(user.id) or sub.class_id != class_id:
        raise HTTPException(status_code=404, detail="Submission not found")

    post = FeedPost(
        submission_id=body.submission_id,
        student_id=str(user.id),
        class_id=class_id,
        content_preview=body.content_preview,
    )
    await post.insert()
    return {"id": str(post.id)}


@router.get("/classes/{class_id}/feed")
async def get_feed(
    class_id: str,
    user: User = Depends(get_current_user),
):
    await _assert_member(class_id, str(user.id))

    posts = await FeedPost.find(
        FeedPost.class_id == class_id,
    ).sort(-FeedPost.created_at).to_list()

    result = []
    for post in posts:
        reactions = await Reaction.find(Reaction.post_id == str(post.id)).to_list()
        result.append({
            "id": str(post.id),
            "submission_id": post.submission_id,
            "student_id": post.student_id,
            "content_preview": post.content_preview,
            "created_at": post.created_at.isoformat(),
            "reactions": [
                {"emoji": r.emoji, "user_id": r.user_id}
                for r in reactions
            ],
        })
    return result


@router.post("/posts/{post_id}/reactions", status_code=status.HTTP_201_CREATED)
async def add_reaction(
    post_id: str,
    body: ReactionRequest,
    user: User = Depends(get_current_user),
):
    post = await FeedPost.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    await _assert_member(post.class_id, str(user.id))

    # One reaction per user per post
    existing = await Reaction.find_one(
        Reaction.post_id == post_id,
        Reaction.user_id == str(user.id),
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate reaction rejected",
        )

    reaction = Reaction(post_id=post_id, user_id=str(user.id), emoji=body.emoji)
    await reaction.insert()
    return {"id": str(reaction.id)}


@router.delete("/posts/{post_id}/reactions")
async def remove_reaction(
    post_id: str,
    user: User = Depends(get_current_user),
):
    existing = await Reaction.find_one(
        Reaction.post_id == post_id,
        Reaction.user_id == str(user.id),
    )
    if existing is None:
        raise HTTPException(status_code=404, detail="Reaction not found")
    await existing.delete()
    return {"removed": True}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    user: User = Depends(get_current_user),
):
    post = await FeedPost.get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Teacher or own post
    is_teacher = bool(user.permissions & MANAGE_CLASS)
    is_own = post.student_id == str(user.id)
    if not (is_teacher or is_own):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    await post.delete()
    return {"deleted": True}


@router.get("/pages/classes/{class_id}/feed", name="feed_page")
@webpage.page("community/feed.html")
async def feed_page(
    request: Request,
    class_id: str,
    user: User = Depends(get_current_user),
):
    await _assert_member(class_id, str(user.id))
    from core.classes.models import Class
    cls = await Class.get(class_id)

    posts = await FeedPost.find(
        FeedPost.class_id == class_id,
    ).sort(-FeedPost.created_at).to_list()

    feed_data = []
    for post in posts:
        reactions = await Reaction.find(Reaction.post_id == str(post.id)).to_list()
        author = await User.get(post.student_id)
        feed_data.append({
            "post": post,
            "author_name": author.display_name if author else post.student_id,
            "reactions": reactions,
            "is_own": post.student_id == str(user.id),
        })

    return {
        "current_user": user,
        "class_id": class_id,
        "class_name": cls.name if cls else class_id,
        "feed": feed_data,
    }
