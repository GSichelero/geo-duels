import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

export const register = createAsyncThunk(
	'users/register',
	async ({ first_name, last_name, nickname, email, password }, thunkAPI) => {
		const body = JSON.stringify({
			first_name,
			last_name,
			nickname,
			email,
			password,
		});

		try {
			const res = await fetch('/api/users/register', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
				},
				body,
			});

			const data = await res.json();

			if (res.status === 201) {
				return data;
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

const getUser = createAsyncThunk('users/me', async (_, thunkAPI) => {
	try {
		const res = await fetch('/api/users/me', {
			method: 'GET',
			headers: {
				Accept: 'application/json',
			},
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

export const login = createAsyncThunk(
	'users/login',
	async ({ email, password }, thunkAPI) => {
		const body = JSON.stringify({
			email,
			password,
		});

		try {
			const res = await fetch('/api/users/login', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
				},
				body,
			});

			const data = await res.json();

			if (res.status === 200) {
				const { dispatch } = thunkAPI;

				dispatch(getUser());

				return data;
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

export const checkAuth = createAsyncThunk(
	'users/verify',
	async (_, thunkAPI) => {
		try {
			const res = await fetch('/api/users/verify', {
				method: 'GET',
				headers: {
					Accept: 'application/json',
				},
			});

			const data = await res.json();

			if (res.status === 200) {
				const { dispatch } = thunkAPI;

				dispatch(getUser());

				return data;
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

export const logout = createAsyncThunk('users/logout', async (_, thunkAPI) => {
	try {
		const res = await fetch('/api/users/logout', {
			method: 'GET',
			headers: {
				Accept: 'application/json',
			},
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

export const getAllUsers = createAsyncThunk('users/get-all-users', async (_, thunkAPI) => {
	try {
		const res = await fetch('/api/users/get-all-users', {
			method: 'GET',
			headers: {
				Accept: 'application/json',
			},
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

export const getFriends = createAsyncThunk('users/get-friends', async (_, thunkAPI) => {
	try {
		const res = await fetch('/api/users/get-friends', {
			method: 'GET',
			headers: {
				Accept: 'application/json',
			},
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

export const getFriendRequestsReceived = createAsyncThunk('users/get-friend-requests-received', async (_, thunkAPI) => {
	try {
		const res = await fetch('/api/users/get-friend-requests-received', {
			method: 'GET',
			headers: {
				Accept: 'application/json',
			},
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

export const getFriendRequestsSent = createAsyncThunk('users/get-friend-requests-sent', async (_, thunkAPI) => {
	try {
		const res = await fetch('/api/users/get-friend-requests-sent', {
			method: 'GET',
			headers: {
				Accept: 'application/json',
			},
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

export const sendFriendRequest = createAsyncThunk(
	'users/send-friend-request',
	async (to_user_id, thunkAPI) => {
		const body = JSON.stringify({
			to_user_id,
		});

		try {
			const res = await fetch('/api/users/send-friend-request', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
				},
				body,
			});

			const data = await res.json();

			if (res.status === 200) {
				try {
					const res = await fetch('/api/users/get-friend-requests-sent', {
						method: 'GET',
						headers: {
							Accept: 'application/json',
						},
					});
			
					const data = await res.json();
			
					if (res.status === 200) {
						return data;
					} else {
						return thunkAPI.rejectWithValue(data);
					}
				} catch (err) {
					return thunkAPI.rejectWithValue(err.response.data);
				}
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

export const acceptFriendRequest = createAsyncThunk(
	'users/accept-friend-request',
	async (request_id, thunkAPI) => {
		const body = JSON.stringify({
			request_id,
		});

		try {
			const res = await fetch('/api/users/accept-friend-request', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
				},
				body,
			});

			const data = await res.json();

			if (res.status === 200) {
				try {
					const res = await fetch('/api/users/get-friends', {
						method: 'GET',
						headers: {
							Accept: 'application/json',
						},
					});
			
					const data = await res.json();
			
					if (res.status === 200) {
						return data;
					} else {
						return thunkAPI.rejectWithValue(data);
					}
				} catch (err) {
					return thunkAPI.rejectWithValue(err.response.data);
				}
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

export const rejectFriendRequest = createAsyncThunk(
	'users/reject-friend-request',
	async (request_id, thunkAPI) => {
		const body = JSON.stringify({
			request_id,
		});

		try {
			const res = await fetch('/api/users/reject-friend-request', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
				},
				body,
			});

			const data = await res.json();

			if (res.status === 200) {
				return data;
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

export const cancelFriendRequest = createAsyncThunk(
	'users/cancel-friend-request',
	async (request_id, thunkAPI) => {
		const body = JSON.stringify({
			request_id,
		});

		try {
			const res = await fetch('/api/users/cancel-friend-request', {
				method: 'POST',
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json',
				},
				body,
			});

			const data = await res.json();

			if (res.status === 200) {
				return data;
			} else {
				return thunkAPI.rejectWithValue(data);
			}
		} catch (err) {
			return thunkAPI.rejectWithValue(err.response.data);
		}
	}
);

export const removeFriend = createAsyncThunk(
	'users/remove-friend',
	async (friend_id, thunkAPI) => {
	const body = JSON.stringify({
		friend_id,
	});

	try {
		const res = await fetch('/api/users/remove-friend', {
			method: 'POST',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
			},
			body,
		});

		const data = await res.json();

		if (res.status === 200) {
			return data;
		} else {
			return thunkAPI.rejectWithValue(data);
		}
	} catch (err) {
		return thunkAPI.rejectWithValue(err.response.data);
	}
});

const initialState = {
	isAuthenticated: false,
	user: null,
	loading: false,
	registered: false,
	previousPath: '/',
	users: [],
	friends: [],
	friendRequestsReceived: [],
	friendRequestsSent: [],
};

const userSlice = createSlice({
	name: 'user',
	initialState,
	reducers: {
		resetRegistered: state => {
			state.registered = false;
		},
	},
	extraReducers: builder => {
		builder
			.addCase(register.pending, state => {
				state.loading = true;
			})
			.addCase(register.fulfilled, state => {
				state.loading = false;
				state.registered = true;
			})
			.addCase(register.rejected, state => {
				state.loading = false;
			})
			.addCase(login.pending, state => {
				state.loading = true;
			})
			.addCase(login.fulfilled, state => {
				state.loading = false;
				state.isAuthenticated = true;
			})
			.addCase(login.rejected, state => {
				state.loading = false;
			})
			.addCase(getUser.pending, state => {
				state.loading = true;
			})
			.addCase(getUser.fulfilled, (state, action) => {
				state.loading = false;
				state.user = action.payload;
			})
			.addCase(getUser.rejected, state => {
				state.loading = false;
			})
			.addCase(checkAuth.pending, state => {
				state.loading = true;
			})
			.addCase(checkAuth.fulfilled, state => {
				state.loading = false;
				state.isAuthenticated = true;
			})
			.addCase(checkAuth.rejected, state => {
				state.loading = false;
			})
			.addCase(logout.pending, state => {
				state.loading = true;
			})
			.addCase(logout.fulfilled, state => {
				state.loading = false;
				state.isAuthenticated = false;
				state.user = null;
			})
			.addCase(logout.rejected, state => {
				state.loading = false;
			})
			.addCase(getAllUsers.pending, state => {
				// state.loading = true;
				state.previousPath = '/users';
			})
			.addCase(getAllUsers.fulfilled, (state, action) => {
				state.loading = false;
				state.users = action.payload;
			})
			.addCase(getAllUsers.rejected, state => {
				state.loading = false;
			})
			.addCase(getFriends.pending, state => {
				// state.loading = true;
				state.previousPath = '/friends';
			})
			.addCase(getFriends.fulfilled, (state, action) => {
				state.loading = false;
				state.friends = action.payload;
			})
			.addCase(getFriends.rejected, state => {
				state.loading = false;
			})
			.addCase(getFriendRequestsReceived.pending, state => {
				// state.loading = true;
				state.previousPath = '/friends';
			})
			.addCase(getFriendRequestsReceived.fulfilled, (state, action) => {
				state.loading = false;
				state.friendRequestsReceived = action.payload;
			})
			.addCase(getFriendRequestsReceived.rejected, state => {
				state.loading = false;
			})
			.addCase(getFriendRequestsSent.pending, state => {
				// state.loading = true;
				state.previousPath = '/friends';
			})
			.addCase(getFriendRequestsSent.fulfilled, (state, action) => {
				state.loading = false;
				state.friendRequestsSent = action.payload;
			})
			.addCase(getFriendRequestsSent.rejected, state => {
				state.loading = false;
			})
			.addCase(sendFriendRequest.pending, state => {
				// state.loading = true;
			})
			.addCase(sendFriendRequest.fulfilled, (state, action) => {
				state.loading = false;
				state.friendRequestsSent = action.payload;
			})
			.addCase(sendFriendRequest.rejected, state => {
				state.loading = false;
			})
			.addCase(acceptFriendRequest.pending, state => {
				// state.loading = true;
			})
			.addCase(acceptFriendRequest.fulfilled, (state, action) => {
				state.loading = false;
				state.friends = action.payload;
				state.friendRequestsReceived = state.friendRequestsReceived.filter(
					request => request.id !== action.meta.arg
				);
			})
			.addCase(acceptFriendRequest.rejected, state => {
				state.loading = false;
			})
			.addCase(rejectFriendRequest.pending, state => {
				// state.loading = true;
			})
			.addCase(rejectFriendRequest.fulfilled, (state, action) => {
				state.loading = false;
				state.friendRequestsReceived = state.friendRequestsReceived.filter(
					request => request.id !== action.meta.arg
				);
			})
			.addCase(rejectFriendRequest.rejected, state => {
				state.loading = false;
			})
			.addCase(cancelFriendRequest.pending, state => {
				// state.loading = true;
			})
			.addCase(cancelFriendRequest.fulfilled, (state, action) => {
				state.loading = false;
				state.friendRequestsSent = state.friendRequestsSent.filter(
					request => request.id !== action.meta.arg
				);
			})
			.addCase(cancelFriendRequest.rejected, state => {
				state.loading = false;
			})
			.addCase(removeFriend.pending, state => {
				// state.loading = true;
			})
			.addCase(removeFriend.fulfilled, (state, action) => {
				state.loading = false;
				state.friends = state.friends.filter(friend => friend.id !== action.meta.arg);
			})
			.addCase(removeFriend.rejected, state => {
				state.loading = false;
			});
	},
});

export const { resetRegistered } = userSlice.actions;
export default userSlice.reducer;
