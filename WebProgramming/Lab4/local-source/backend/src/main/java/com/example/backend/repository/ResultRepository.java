package com.example.backend.repository;

import com.example.backend.entity.Result;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ResultRepository extends JpaRepository<Result, Long> {
    List<Result> findAllByOrderByTimestampDesc();
}