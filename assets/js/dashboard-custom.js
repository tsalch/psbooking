function readyMain() {
	const triggers = document.getElementsByClassName('dashboard-responsive-nav-trigger')
	for (const trigger of triggers) {
		trigger.onclick = function (e) {
			const menuItems = document.getElementsByClassName('dashboard-nav')
			for (const menuItem of menuItems) {
				menuItem.classList.toggle('active')
			}
			e.preventDefault()
		}
	}
}

document.addEventListener("DOMContentLoaded", readyMain)