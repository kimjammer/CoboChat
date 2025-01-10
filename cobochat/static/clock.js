// Set initial time
document.documentElement.style.setProperty('--timer-day', "'" + 0);
document.documentElement.style.setProperty('--timer-hours', "'" + 0);
document.documentElement.style.setProperty('--timer-minutes', "'" + 0);
document.documentElement.style.setProperty('--timer-seconds', "'" + 0);

var deadline = new Date('March 23, 2025 17:00:00');

let x = setInterval(function () {

    let now = new Date().getTime();

    let t = deadline - now;

    let days = Math.floor(t / (1000 * 60 * 60 * 24));
    let hours = Math.floor(
        (t % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let minutes = Math.floor(
        (t % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor(
        (t % (1000 * 60)) / 1000);
    
    document.documentElement.style.setProperty('--timer-day', "'" + days);
    document.documentElement.style.setProperty('--timer-hours', "'" + hours);
    document.documentElement.style.setProperty('--timer-minutes', "'" + minutes);
    document.documentElement.style.setProperty('--timer-seconds', "'" + seconds);

    // Output for over time
    if (t < 0) {
        clearInterval(x);
        document.documentElement.style.setProperty('--timer-day', "'" + 0);
        document.documentElement.style.setProperty('--timer-hours', "'" + 0);
        document.documentElement.style.setProperty('--timer-minutes', "'" + 0);
        document.documentElement.style.setProperty('--timer-seconds', "'" + 0);
    }
}, 1000);