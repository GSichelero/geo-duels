const express = require('express');
const fetch = (...args) =>
	import('node-fetch').then(({ default: fetch }) => fetch(...args));

const router = express.Router();

router.post('/api/users/create-room', async (req, res) => {
    const { access } = req.cookies;
    const { room_name, room_password, max_members, number_of_rounds, time_per_pick, time_per_guess, moving_allowed } = req.body;
    const body = JSON.stringify({
        room_name,
        room_password,
        max_members,
        number_of_rounds,
        time_per_pick,
        time_per_guess,
        moving_allowed,
    });
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/create-room`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body,
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

router.post('/api/users/create-single-player-room', async (req, res) => {
    const { room_name, room_password, max_members, number_of_rounds, time_per_pick, time_per_guess, moving_allowed } = req.body;
    const body = JSON.stringify({
        room_name,
        room_password,
        max_members,
        number_of_rounds,
        time_per_pick,
        time_per_guess,
        moving_allowed,
    });
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/create-single-player-room`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body,
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

router.post('/api/users/invite-friend', async (req, res) => {
    const { access } = req.cookies;
    const { friend_username, room_id } = req.body;
    const body = JSON.stringify({
        friend_username,
        room_id,
    });
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/invite-friend`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body,
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});


router.get('/api/users/get-received-invites', async (req, res) => {
    const { access } = req.cookies;
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/get-received-invites`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

router.post('/api/users/reject-invite', async (req, res) => {
    const { access } = req.cookies;
    const { room_id } = req.body;
    const body = JSON.stringify({
        room_id,
    });
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/reject-invite`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body,
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

router.post('/api/users/join-room', async (req, res) => {
    const { access } = req.cookies;
    const { room_name, room_password } = req.body;
    const body = JSON.stringify({
        room_name,
        room_password,
    });
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/join-room`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body,
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

router.post('/api/users/join-single-player-room', async (req, res) => {
    const { room_name, room_password } = req.body;
    const body = JSON.stringify({
        room_name,
        room_password,
    });
    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/join-single-player-room`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body,
        });
        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

module.exports = router;