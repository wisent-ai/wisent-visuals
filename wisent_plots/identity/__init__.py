"""What a repository is allowed to say about itself on a banner.

The profile reads a repository's own metadata; the two tables beside it record
which titles and descriptions a person approved, and which ones were withdrawn.
"""

from .profile import BannerIdentity, RepositoryProfile, generate_identity

__all__ = ["BannerIdentity", "RepositoryProfile", "generate_identity"]
