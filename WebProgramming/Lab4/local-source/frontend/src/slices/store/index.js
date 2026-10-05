import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../authSlice';
import pointReducer from '../pointSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        points: pointReducer,
    },
});