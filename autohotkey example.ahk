#SingleInstance Force		; Allow reloading the script by double-clicking it
#NoEnv						; Prevent environment variables from interfering
#Warn						; Warn on issues
SendMode Input				; Compatibility


; Specify the actual key to be pressed...

F11::
	send_a(7)
	send_b(3)
	return


; Functions...

send_a(n) {
	loop %n% {
		send Help me I am trapped in a script{!}
		sleep 10
		send {Return}
		sleep 10
	}
}

send_b(n) {
	loop %n% {
		send Uh nevermind.
		sleep 10
		send {Return}
		sleep 10
	}
}
