package com.example.backend.controller;

import com.example.backend.dto.PointDto;
import com.example.backend.entity.Result;
import com.example.backend.service.PointService;
import com.example.backend.service.ResultService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class PointController {
    private final PointService pointService;
    private final ResultService resultService;

    public PointController(PointService pointService, ResultService resultService) {
        this.pointService = pointService;
        this.resultService = resultService;
    }

    @PostMapping("/check")
    public ResponseEntity<Result> check(@Valid @RequestBody PointDto dto) {
        return ResponseEntity.ok(pointService.checkPoint(dto));
    }

    @GetMapping("/results")
    public ResponseEntity<List<Result>> getResults() {
        List<Result> results = resultService.getResults();
        return ResponseEntity.ok(results);
    }

    @DeleteMapping("/results")
    public ResponseEntity<String> clearResults() {
        resultService.clearResults();
        return ResponseEntity.ok("Results cleared");
    }
}