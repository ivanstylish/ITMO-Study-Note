import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = '/lab4/api/auth';
axios.defaults.withCredentials = true;

export const login = createAsyncThunk('auth/login', async ({ username, password }, { rejectWithValue }) => {
    try {
        const response = await axios.post(`${API_URL}/login`, { username, password });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response?.data || 'Login error');
    }
});

export const register = createAsyncThunk('auth/register', async ({ username, password }, { rejectWithValue }) => {
    try {
        const response = await axios.post(`${API_URL}/register`, { username, password });
        return response.data;
    } catch (error) {
        return rejectWithValue(error.response?.data || 'Registration error');
    }
});

export const logout = createAsyncThunk('auth/logout', async () => {
    await axios.post(`${API_URL}/logout`);
    return true;
});

const authSlice = createSlice({
    name: 'auth',
    initialState: {
        isAuthenticated: false,
        status: 'idle',
        error: null
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(login.fulfilled, (state) => {
                state.isAuthenticated = true;
                state.error = null;
            })
            .addCase(login.rejected, (state, action) => {
                state.isAuthenticated = false;
                state.error = action.payload;
            })
            .addCase(register.fulfilled, (state) => {
                state.status = 'registered';
                state.error = null;
            })
            .addCase(register.rejected, (state, action) => {
                state.status = 'idle';
                state.error = action.payload;
            })
            .addCase(logout.fulfilled, (state) => {
                state.isAuthenticated = false;
            });
    },
});

export default authSlice.reducer;