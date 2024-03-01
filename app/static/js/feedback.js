function showChallengeDropdown(value) {
    var challengeDropdown = document.getElementById('challenge-dropdown');
    if (value === 'challenge') {
        challengeDropdown.style.display = 'block';
    } else {
        challengeDropdown.style.display = 'none';
    }
}
