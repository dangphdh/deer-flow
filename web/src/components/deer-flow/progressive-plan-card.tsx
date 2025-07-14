// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";
import { useTranslations } from "next-intl";
import React, { useMemo, useState, useCallback } from "react";

import { Markdown } from "./markdown";
import { RainbowText } from "./rainbow-text";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import type { Message, Option } from "~/core/messages";
import { parseJSON } from "~/core/utils";
import { cn } from "~/lib/utils";

const GREETINGS = ["Cool", "Sounds great", "Looks good", "Great", "Awesome"];

interface ProgressivePlanCardProps {
  className?: string;
  message: Message;
  interruptMessage?: Message | null;
  onFeedback?: (feedback: { option: Option }) => void;
  onSendMessage?: (
    message: string,
    options?: { interruptFeedback?: string },
  ) => void;
  waitForFeedback?: boolean;
}

export function ProgressivePlanCard({
  className,
  message,
  interruptMessage,
  onFeedback,
  waitForFeedback,
  onSendMessage,
}: ProgressivePlanCardProps) {
  const t = useTranslations("chat.research");
  
  // Memoize plan parsing with optimized checks
  const plan = useMemo<{
    title?: string;
    thought?: string;
    steps?: { title?: string; description?: string }[];
  }>(() => {
    // Early return if no content
    if (!message.content?.trim()) {
      return {};
    }
    
    // Quick check if content looks like JSON
    const content = message.content.trim();
    if (!content.startsWith('{') && !content.startsWith('{"')) {
      return {};
    }
    
    try {
      return parseJSON(message.content, {});
    } catch {
      // Return partial content for display
      return { thought: "Planning in progress..." };
    }
  }, [message.content]);

  const reasoningContent = message.reasoningContent;
  const hasReasoningContent = Boolean(reasoningContent?.trim());
  const hasMainContent = Boolean(message.content?.trim());
  
  // Show progressive states
  const isInitialThinking = hasReasoningContent && !hasMainContent;
  const isProcessingPlan = hasMainContent && message.isStreaming;
  const isPlanComplete = hasMainContent && !message.isStreaming;
  
  // Show thought content immediately when available
  const shouldShowThoughts = hasReasoningContent;
  
  // Show plan structure as soon as we have any JSON content
  const shouldShowPlan = hasMainContent;

  const handleAccept = useCallback(async () => {
    if (onSendMessage) {
      onSendMessage(
        `${GREETINGS[Math.floor(Math.random() * GREETINGS.length)]}! ${Math.random() > 0.5 ? "Let's get started." : "Let's start."}`,
        {
          interruptFeedback: "accepted",
        },
      );
    }
  }, [onSendMessage]);

  return (
    <div className={cn("w-full space-y-4", className)}>
      {/* Progressive Thinking Indicator */}
      {isInitialThinking && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="flex items-center gap-2 text-sm text-muted-foreground"
        >
          <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
          <RainbowText animated={true}>AI is thinking about your request...</RainbowText>
        </motion.div>
      )}

      {/* Processing Indicator */}
      {isProcessingPlan && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="flex items-center gap-2 text-sm text-muted-foreground"
        >
          <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
          <RainbowText animated={true}>Creating detailed research plan...</RainbowText>
        </motion.div>
      )}

      {/* Plan Card */}
      {shouldShowPlan && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          <Card className="w-full">
            <CardHeader>
              <CardTitle>
                <Markdown animated={message.isStreaming}>
                  {`### ${
                    plan.title || t("deepResearch")
                  }`}
                </Markdown>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {plan.thought && (
                <Markdown className="opacity-80 mb-4" animated={message.isStreaming}>
                  {plan.thought}
                </Markdown>
              )}
              
              {plan.steps && plan.steps.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-muted-foreground">
                    Research Steps ({plan.steps.length})
                  </h4>
                  <div className="border-l-2 border-primary/20 pl-6 space-y-4">
                    {plan.steps.map((step, i) => (
                      <motion.div
                        key={`step-${i}`}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1, duration: 0.2 }}
                        className="space-y-1"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-sm font-medium text-primary">{i + 1}.</span>
                          <div className="flex-1">
                            <h3 className="text-base font-medium">
                              <Markdown animated={message.isStreaming}>
                                {step.title || `Step ${i + 1}`}
                              </Markdown>
                            </h3>
                            {step.description && (
                              <div className="text-muted-foreground text-sm mt-1">
                                <Markdown animated={message.isStreaming}>
                                  {step.description}
                                </Markdown>
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Loading placeholder for incomplete plans */}
              {message.isStreaming && (!plan.steps || plan.steps.length === 0) && (
                <div className="space-y-2">
                  <div className="h-4 bg-muted rounded animate-pulse" />
                  <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  <div className="h-4 bg-muted rounded animate-pulse w-1/2" />
                </div>
              )}
            </CardContent>
            
            {/* Action Buttons */}
            <CardFooter className="flex justify-end">
              {isPlanComplete && interruptMessage?.options?.length && (
                <motion.div
                  className="flex gap-2"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                >
                  {interruptMessage.options.map((option) => (
                    <Button
                      key={option.value}
                      variant={
                        option.value === "accepted" ? "default" : "outline"
                      }
                      disabled={!waitForFeedback}
                      onClick={() => {
                        if (option.value === "accepted") {
                          void handleAccept();
                        } else {
                          onFeedback?.({
                            option,
                          });
                        }
                      }}
                    >
                      {option.text}
                    </Button>
                  ))}
                </motion.div>
              )}
              
              {/* Processing state indicator */}
              {isProcessingPlan && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
                  <span>Finalizing plan...</span>
                </div>
              )}
            </CardFooter>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
