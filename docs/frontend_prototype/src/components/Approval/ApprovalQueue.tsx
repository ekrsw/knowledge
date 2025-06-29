import React from 'react';
import { Clock, Eye, Edit, X, CheckCircle, AlertCircle } from 'lucide-react';
import { FAQ } from '../../types';
import { mockCategories } from '../../data/mockData';

interface ApprovalQueueProps {
  pendingFAQs: FAQ[];
  onApprove: (faq: FAQ) => void;
  onReject: (faq: FAQ) => void;
  onEdit: (faq: FAQ) => void;
  onView: (faq: FAQ) => void;
}

export const ApprovalQueue: React.FC<ApprovalQueueProps> = ({
  pendingFAQs,
  onApprove,
  onReject,
  onEdit,
  onView,
}) => {
  const getCategoryColor = (categoryName: string) => {
    const category = mockCategories.find(c => c.name === categoryName);
    return category?.color || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (pendingFAQs.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <Clock className="mr-2" size={24} />
            承認待ちFAQ一覧
          </h2>
        </div>
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <CheckCircle size={48} className="mx-auto" />
          </div>
          <p className="text-gray-500 text-lg">承認待ちのFAQはありません</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 flex items-center">
          <Clock className="mr-2" size={24} />
          承認待ちFAQ一覧
        </h2>
        <p className="text-gray-600 mt-2">承認が必要な投稿: {pendingFAQs.length}件</p>
      </div>

      <div className="divide-y divide-gray-100">
        {pendingFAQs.map((faq) => (
          <div key={faq.id} className="p-6 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-2">
                  {faq.isImportant && (
                    <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
                  )}
                  <span className="text-sm font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded">
                    {faq.articleNumber}
                  </span>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                    新規
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(faq.category)}`}>
                    {faq.category}
                  </span>
                </div>

                <div className="mb-2">
                  <span className="text-sm text-gray-600">投稿者:</span>
                  <span className="ml-2 font-medium text-gray-900">{faq.authorName}</span>
                  <span className="ml-4 text-sm text-gray-600">投稿日:</span>
                  <span className="ml-2 text-gray-900">{formatDate(faq.createdAt)}</span>
                </div>

                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  {faq.title}
                </h4>

                <p className="text-gray-600 line-clamp-2 mb-3">
                  {faq.question}
                </p>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={() => onView(faq)}
                  className="flex items-center bg-blue-100 text-blue-700 px-3 py-2 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                >
                  <Eye className="mr-1" size={16} />
                  詳細・承認
                </button>
                <button
                  onClick={() => onEdit(faq)}
                  className="flex items-center bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                >
                  <Edit className="mr-1" size={16} />
                  編集
                </button>
                <button
                  onClick={() => onReject(faq)}
                  className="flex items-center bg-red-100 text-red-700 px-3 py-2 rounded-lg hover:bg-red-200 transition-colors text-sm"
                >
                  <X className="mr-1" size={16} />
                  却下
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};