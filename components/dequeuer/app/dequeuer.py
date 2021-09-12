from __future__ import annotations
from austin_heller_repo.api_interface import ApiInterfaceFactory


class Dequeuer():

	def __init__(self, *, dequeuer_guid: str, queue_guid: str, api_interface_factory: Api):