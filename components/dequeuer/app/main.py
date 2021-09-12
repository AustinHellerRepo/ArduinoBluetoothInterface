import sys
from app.dequeuer import Dequeuer
from austin_heller_repo.socket_client_factory import get_machine_guid


if len(sys.argv) != 2:
	_error = "Must provide queue guid as argument to script."
	print(_error)
	raise Exception(_error)
else:

	_queue_guid = sys.argv[1]


	_dequeuer_guid = get_machine_guid()

	_dequeuer = Dequeuer(
		dequeuer_guid=_dequeuer_guid,
		queue_guid=
	)





