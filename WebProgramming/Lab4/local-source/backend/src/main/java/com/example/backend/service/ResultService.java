package com.example.backend.service;

import com.example.backend.entity.Result;
import com.example.backend.repository.ResultRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.DeleteMapping;

import java.util.List;

@Service
public class ResultService {
    private final ResultRepository resultRepository;

    public ResultService(ResultRepository resultRepository) {
        this.resultRepository = resultRepository;
    }

    public List<Result> getResults() {
        return resultRepository.findAllByOrderByTimestampDesc();
    }

    @DeleteMapping("/results")
    public ResponseEntity<String> clearResults() {
        resultRepository.deleteAll();
        return ResponseEntity.ok("All results cleared");
    }
}