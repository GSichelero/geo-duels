const express = require('express');
const fetch = (...args) =>
	import('node-fetch').then(({ default: fetch }) => fetch(...args));

const router = express.Router();

router.get('/api/users/get-friends', async (req, res) => {
    const { access } = req.cookies;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/get-friends`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${access}`,
            }
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to get all friends',
        });
    }
});

router.get('/api/users/get-friend-requests-sent', async (req, res) => {
    const { access } = req.cookies;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/get-friend-requests-sent`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${access}`,
            }
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to get all friend requests sent',
        });
    }
});

router.get('/api/users/get-friend-requests-received', async (req, res) => {
    const { access } = req.cookies;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/get-friend-requests-received`, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${access}`,
            }
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to get all friend requests received',
        });
    }
});

router.post('/api/users/send-friend-request', async (req, res) => {
    const { access } = req.cookies;
    const { to_user_id } = req.body;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/send-friend-request`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ to_user_id }),
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to send a friend request',
        });
    }
});

router.post('/api/users/accept-friend-request', async (req, res) => {
    const { access } = req.cookies;
    const { request_id } = req.body;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/accept-friend-request`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ request_id }),
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to accept a friend request',
        });
    }
});

router.post('/api/users/reject-friend-request', async (req, res) => {
    const { access } = req.cookies;
    const { request_id } = req.body;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/reject-friend-request`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ request_id }),
        });

        const data = await apiRes.json();
        
        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to reject a friend request',
        });
    }
});

router.post('/api/users/cancel-friend-request', async (req, res) => {
    const { access } = req.cookies;
    const { request_id } = req.body;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/cancel-friend-request`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ request_id }),
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to cancel a friend request',
        });
    }
});

router.post('/api/users/remove-friend', async (req, res) => {
    const { access } = req.cookies;
    const { friend_id } = req.body;

    try {
        const apiRes = await fetch(`${process.env.API_URL}/api/users/remove-friend`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ friend_id }),
        });

        const data = await apiRes.json();

        return res.status(apiRes.status).json(data);
    } catch (err) {
        return res.status(500).json({
            error: 'Something went wrong when trying to remove a friend',
        });
    }
});

module.exports = router;