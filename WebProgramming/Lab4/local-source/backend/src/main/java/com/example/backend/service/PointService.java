package com.example.backend.service;

import com.example.backend.dto.PointDto;
import com.example.backend.entity.Result;
import com.example.backend.repository.ResultRepository;
import com.example.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class PointService {
    private final ResultRepository resultRepository;

    public PointService(ResultRepository resultRepository, UserRepository userRepository) {
        this.resultRepository = resultRepository;
    }

    public Result checkPoint(PointDto dto) {
        double x = dto.getX();
        double y = dto.getY();
        double r = dto.getR();

        boolean hit = isHit(x, y, r);

        Result result = new Result();
        result.setX(x);
        result.setY(y);
        result.setR(r);
        result.setHit(hit);
        result.setTimestamp(LocalDateTime.now());

        return resultRepository.saveAndFlush(result);
    }

    private boolean isHit(double x, double y, double r) {
        double absR = Math.abs(r);

        if (x >= 0 && y >= 0) {
            return (x + y) <= absR;
        }

        if (x <= 0 && x >= -absR / 2 && y <= 0 && y >= -absR) {
            return true;
        }

        if (x >= 0 && y <= 0) {
            return (x * x + y * y) <= (absR * absR);
        }

        return false;
    }
}