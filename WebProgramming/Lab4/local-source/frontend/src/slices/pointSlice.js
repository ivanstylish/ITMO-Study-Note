import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = '/lab4/api';

axios.defaults.withCredentials = true;

export const fetchResults = createAsyncThunk(
    'points/fetchResults',
    async (_, { rejectWithValue }) => {
        try {
            const response = await axios.get(`${API_URL}/results`);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data?.message || 'Failed to fetch results');
        }
    }
);

export const checkPoint = createAsyncThunk(
    'points/checkPoint',
    async (pointDto, { rejectWithValue }) => {
        try {
            const payload = {
                x: parseFloat(pointDto.x),
                y: parseFloat(pointDto.y),
                r: parseFloat(pointDto.r)
            };

            const response = await axios.post(`${API_URL}/check`, payload);
            return response.data;
        } catch (error) {
            return rejectWithValue(error.response?.data?.message || 'Failed to check point');
        }
    }
);

export const clearRemoteResults = createAsyncThunk(
    'points/clearRemoteResults',
    async (_, { rejectWithValue }) => {
        try {
            await axios.delete(`${API_URL}/results`);
            return [];
        } catch (error) {
            return rejectWithValue('Failed to clear results');
        }
    }
);

const pointSlice = createSlice({
    name: 'points',
    initialState: {
        list: [],
        r: 1,
        status: 'idle',
        error: null,
    },
    reducers: {
        setR: (state, action) => {
            state.r = parseFloat(action.payload);
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchResults.fulfilled, (state, action) => {
                state.list = Array.isArray(action.payload) ? action.payload : [];
            })
            .addCase(checkPoint.fulfilled, (state, action) => {
                state.list.unshift(action.payload);
            })
            .addCase(clearRemoteResults.fulfilled, (state) => {
                state.list = [];
            });
    },
});

export const { setR } = pointSlice.actions;
export default pointSlice.reducer;