import React, { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy
} from '@dnd-kit/sortable';
import { Plus } from 'lucide-react';
import TaskCard from './TaskCard';

const KanbanColumn = ({ title, subtitle, count, tasks, status }) => {
  return (
    <div className="flex-1 min-w-[280px] max-w-[400px]">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
        <span className="text-xs font-medium text-accent-cyan bg-accent-cyan/10 px-2 py-0.5 rounded-full">
          {count}
        </span>
      </div>

      <div className="bg-dark-800/50 rounded-xl border border-white/5 p-3 min-h-[200px]">
        <SortableContext items={tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-gray-600 text-sm">
              Drop tasks here
            </div>
          ) : (
            tasks.map(task => <TaskCard key={task.id} task={task} />)
          )}
        </SortableContext>
      </div>
    </div>
  );
};

const KanbanBoard = ({ wsData }) => {
  const [tasks, setTasks] = useState([]);
  const [activeId, setActiveId] = useState(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    if (wsData) {
      if (wsData.type === 'task_created' || wsData.type === 'task_updated' || wsData.type === 'task_deleted') {
        fetchTasks();
      }
    }
  }, [wsData]);

  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/tasks');
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  const handleDragEnd = async (event) => {
    const { active, over } = event;

    if (!over) return;

    const activeTask = tasks.find(t => t.id === active.id);
    const overTask = tasks.find(t => t.id === over.id);

    if (activeTask && overTask) {
      // Moving within same column
      if (activeTask.status === overTask.status) {
        setTasks((items) => {
          const oldIndex = items.findIndex(i => i.id === active.id);
          const newIndex = items.findIndex(i => i.id === over.id);
          return arrayMove(items, oldIndex, newIndex);
        });
      } else {
        // Moving to different column
        const newStatus = overTask.status;
        await updateTaskStatus(active.id, newStatus);
      }
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      await fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchTasks();
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const permanentTasks = tasks.filter(t => t.status === 'permanent');
  const backlogTasks = tasks.filter(t => t.status === 'backlog');
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  const createSampleTasks = async () => {
    const sampleTasks = [
      {
        title: 'Daily health check',
        description: 'Monitor system health and performance metrics',
        status: 'permanent',
        priority: 'medium',
        task_type: 'health_check',
        is_recurring: 1
      },
      {
        title: 'Weekly backup verification',
        description: 'Verify all backups completed successfully',
        status: 'permanent',
        priority: 'medium',
        task_type: 'backup',
        is_recurring: 7
      },
      {
        title: 'API integration testing',
        description: 'Test new endpoints for agent data ingestion',
        status: 'backlog',
        priority: 'high',
        task_type: 'custom',
        is_recurring: 0
      },
      {
        title: 'Update dashboard UI',
        description: 'Implement new design for metrics cards',
        status: 'in_progress',
        priority: 'high',
        task_type: 'custom',
        is_recurring: 0
      }
    ];

    for (const task of sampleTasks) {
      await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
      });
    }
    fetchTasks();
  };

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Task Board</h2>
          <p className="text-sm text-gray-500">Drag tasks between columns to update status</p>
        </div>
        <button
          onClick={createSampleTasks}
          className="flex items-center gap-2 px-4 py-2 bg-accent-purple hover:bg-accent-purple/80 text-white rounded-lg text-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Sample Tasks
        </button>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4">
          <KanbanColumn
            title="Permanent"
            subtitle="Recurring tasks (daily checks, etc.)"
            count={permanentTasks.length}
            tasks={permanentTasks}
            status="permanent"
          />
          <KanbanColumn
            title="Backlog"
            subtitle="Waiting to be worked on"
            count={backlogTasks.length}
            tasks={backlogTasks}
            status="backlog"
          />
          <KanbanColumn
            title="In Progress"
            subtitle="Agent is working on this"
            count={inProgressTasks.length}
            tasks={inProgressTasks}
            status="in_progress"
          />
          {completedTasks.length > 0 && (
            <KanbanColumn
              title="Completed"
              subtitle="Recently finished tasks"
              count={completedTasks.length}
              tasks={completedTasks}
              status="completed"
            />
          )}
        </div>
      </DndContext>
    </div>
  );
};

export default KanbanBoard;
