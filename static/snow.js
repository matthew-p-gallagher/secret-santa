document.addEventListener('DOMContentLoaded', function () {
	// Create canvas element
	const canvas = document.createElement('canvas');
	canvas.id = 'snowCanvas';
	document.body.prepend(canvas);

	const ctx = canvas.getContext('2d');

	// Set canvas size
	function setCanvasSize() {
		canvas.width = window.innerWidth;
		canvas.height = window.innerHeight;
	}

	setCanvasSize();
	window.addEventListener('resize', setCanvasSize);

	// Snowflake class
	class Snowflake {
		constructor() {
			this.reset(true);
		}

		reset(isInitial = false) {
			this.x = Math.random() * canvas.width;
			this.y = isInitial ? -(Math.random() * canvas.height) : -10;
			this.size = Math.random() * 3 + 1;
			this.speed = Math.random() * 1 + 0.5;
			this.wobble = Math.random() * 2 - 1;
			this.opacity = Math.random() * 0.5 + 0.5;
		}

		update() {
			this.y += this.speed;
			this.x += this.wobble;

			// Reset if snowflake goes off screen
			if (this.y > canvas.height + 10) {
				this.reset();
			}
		}

		draw() {
			ctx.beginPath();
			ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
			ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
			ctx.fill();
		}
	}

	// Create snowflakes
	const snowflakes = Array(60)
		.fill(null)
		.map(() => new Snowflake());

	// Animation loop
	function animate() {
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		snowflakes.forEach((snowflake) => {
			snowflake.update();
			snowflake.draw();
		});

		requestAnimationFrame(animate);
	}

	animate();
});
