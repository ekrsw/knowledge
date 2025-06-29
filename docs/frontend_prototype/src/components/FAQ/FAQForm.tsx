import React, { useState } from 'react';
import { Save, Send, X, AlertCircle } from 'lucide-react';
import { FAQ } from '../../types';
import { mockCategories, mockApprovalGroups } from '../../data/mockData';

interface FAQFormProps {
  faq?: FAQ;
  onSave: (faq: Partial<FAQ>) => void;
  onCancel: () => void;
  isEditing?: boolean;
}

export const FAQForm: React.FC<FAQFormProps> = ({
  faq,
  onSave,
  onCancel,
  isEditing = false,
}) => {
  const [formData, setFormData] = useState({
    articleNumber: faq?.articleNumber || '',
    title: faq?.title || '',
    category: faq?.category || '',
    approvalGroup: faq?.approvalGroup || '',
    keywords: faq?.keywords.join(', ') || '',
    isImportant: faq?.isImportant || false,
    publicStartDate: faq?.publicStartDate || new Date().toISOString().split('T')[0],
    publicEndDate: faq?.publicEndDate || new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    question: faq?.question || '',
    answer: faq?.answer || '',
    additionalComment: faq?.additionalComment || '',
    notes: faq?.notes || '',
  });

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (isDraft: boolean = false) => {
    const faqData: Partial<FAQ> = {
      ...formData,
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k),
      status: isDraft ? 'draft' : 'pending',
    };
    onSave(faqData);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">
          {isEditing ? 'FAQ編集' : 'FAQ投稿'}
        </h2>
      </div>

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              記事番号
            </label>
            <input
              type="text"
              value={formData.articleNumber}
              onChange={(e) => handleInputChange('articleNumber', e.target.value)}
              placeholder="KBA-00000-"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">※既存番号で修正投稿可能</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              タイトル <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              情報カテゴリ <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.category}
              onChange={(e) => handleInputChange('category', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">選択してください</option>
              {mockCategories.map((category) => (
                <option key={category.id} value={category.name}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              承認グループ
            </label>
            <select
              value={formData.approvalGroup}
              onChange={(e) => handleInputChange('approvalGroup', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">未設定</option>
              {mockApprovalGroups.map((group) => (
                <option key={group.id} value={group.name}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              キーワード
            </label>
            <input
              type="text"
              value={formData.keywords}
              onChange={(e) => handleInputChange('keywords', e.target.value)}
              placeholder="キーワードをカンマ区切りで入力"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="isImportant"
              checked={formData.isImportant}
              onChange={(e) => handleInputChange('isImportant', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="isImportant" className="ml-2 flex items-center text-sm text-gray-700">
              <AlertCircle className="mr-1 text-red-500" size={16} />
              重要
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              公開期限(開始)
            </label>
            <input
              type="date"
              value={formData.publicStartDate}
              onChange={(e) => handleInputChange('publicStartDate', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              公開期限(終了)
            </label>
            <input
              type="date"
              value={formData.publicEndDate}
              onChange={(e) => handleInputChange('publicEndDate', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            質問 <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.question}
            onChange={(e) => handleInputChange('question', e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            回答 <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.answer}
            onChange={(e) => handleInputChange('answer', e.target.value)}
            rows={6}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            追加コメント
          </label>
          <textarea
            value={formData.additionalComment}
            onChange={(e) => handleInputChange('additionalComment', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            備考
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => handleInputChange('notes', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="flex flex-col sm:flex-row gap-3 justify-end">
          <button
            onClick={() => handleSubmit(true)}
            className="flex items-center justify-center px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Save className="mr-2" size={18} />
            下書き保存
          </button>
          <button
            onClick={() => handleSubmit(false)}
            className="flex items-center justify-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Send className="mr-2" size={18} />
            投稿
          </button>
          <button
            onClick={onCancel}
            className="flex items-center justify-center px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <X className="mr-2" size={18} />
            キャンセル
          </button>
        </div>
      </div>
    </div>
  );
};